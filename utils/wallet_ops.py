import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, CommandHandler, CallbackQueryHandler
from solana.rpc.api import Client
from solana.transaction import Transaction
from solana.publickey import PublicKey
from solana.system_program import TransferParams, transfer
from spl.token.instructions import transfer_checked, get_associated_token_address
from utils.signer import load_wallet_from_env

SOLANA_RPC = os.getenv("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com")
client = Client(SOLANA_RPC)
WITHDRAW_ALL_STATE = {}

# SPL token info
SPL_TOKENS = {
    "USDC": {
        "mint": PublicKey("EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"),
        "decimals": 6,
    },
    "wSOL": {
        "mint": PublicKey("So11111111111111111111111111111111111111112"),
        "decimals": 9,
    },
}

def withdraw_all(update: Update, context: CallbackContext):
    if not context.args:
        update.message.reply_text("❌ Usage: /withdrawall <destination_wallet_address>")
        return

    dest = context.args[0]
    if not dest or len(dest) < 32:
        update.message.reply_text("❌ Invalid wallet address.")
        return

    WITHDRAW_ALL_STATE[update.effective_chat.id] = dest
    buttons = [
        [
            InlineKeyboardButton("✅ Confirm", callback_data="confirm_withdraw_all"),
            InlineKeyboardButton("❌ Cancel", callback_data="cancel_withdraw_all")
        ]
    ]
    update.message.reply_text(
        f"Are you sure you want to withdraw all funds (SOL + SPL tokens) to:\n<code>{dest}</code>?",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

def handle_withdraw_all(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    user_id = query.message.chat_id
    action = query.data

    if action == "cancel_withdraw_all":
        query.edit_message_text("❌ Withdraw cancelled.")
        return

    if action == "confirm_withdraw_all":
        dest = WITHDRAW_ALL_STATE.get(user_id)
        if not dest:
            query.edit_message_text("❌ No destination found.")
            return

        try:
            kp = load_wallet_from_env()
            src_pub = kp.public_key
            dest_pub = PublicKey(dest)
            tx = Transaction()

            # SOL transfer
            sol_balance = client.get_balance(src_pub)["result"]["value"]
            if sol_balance > 5000:
                tx.add(
                    transfer(
                        TransferParams(
                            from_pubkey=src_pub,
                            to_pubkey=dest_pub,
                            lamports=sol_balance - 5000
                        )
                    )
                )

            # SPL token transfers
            for token, info in SPL_TOKENS.items():
                ata = get_associated_token_address(src_pub, info["mint"])
                result = client.get_token_account_balance(ata)
                amount = float(result.get("result", {}).get("value", {}).get("uiAmount", 0))
                if amount > 0:
                    tx.add(
                        transfer_checked(
                            program_id=PublicKey("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"),
                            source=ata,
                            mint=info["mint"],
                            dest=get_associated_token_address(dest_pub, info["mint"]),
                            owner=src_pub,
                            amount=int(amount * (10 ** info["decimals"])),
                            decimals=info["decimals"]
                        )
                    )

            tx_sig = client.send_transaction(tx, kp)["result"]
            query.edit_message_text(
                f"✅ Withdrawal initiated to <code>{dest}</code>\n"
                f"🔗 <a href='https://solscan.io/tx/{tx_sig}'>View on Solscan</a>",
                parse_mode="HTML"
            )

        except Exception as e:
            query.edit_message_text(f"❌ Error: {e}")

# === Add to dispatcher in main.py ===
withdraw_all_handler = CommandHandler("withdrawall", withdraw_all)
confirm_all_handler = CallbackQueryHandler(handle_withdraw_all, pattern="^confirm_withdraw_all|cancel_withdraw_all$")
