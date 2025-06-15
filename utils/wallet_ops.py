import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, CommandHandler, CallbackQueryHandler
from solana.publickey import PublicKey
from solana.transaction import Transaction
from solana.system_program import TransferParams, transfer
from spl.token.instructions import transfer_checked, get_associated_token_address
from spl.token.constants import TOKEN_PROGRAM_ID
from solana.rpc.api import Client
from utils.signer import load_wallet_from_env

SOLANA_RPC = os.getenv("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com")
client = Client(SOLANA_RPC)
WITHDRAW_STATE = {}

# Supported SPL Tokens
SPL_TOKENS = {
    "USDC": {
        "mint": PublicKey("EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"),
        "decimals": 6
    },
    "wSOL": {
        "mint": PublicKey("So11111111111111111111111111111111111111112"),
        "decimals": 9
    }
}

def withdraw_all(update: Update, context: CallbackContext):
    if not context.args:
        update.message.reply_text("❌ Usage: /withdrawall <destination_wallet_address>")
        return
    dest = context.args[0]
    if not dest or len(dest) < 32:
        update.message.reply_text("❌ Invalid wallet address.")
        return

    WITHDRAW_STATE[update.effective_chat.id] = dest
    buttons = [
        [
            InlineKeyboardButton("✅ Confirm", callback_data="confirm_withdraw_all"),
            InlineKeyboardButton("❌ Cancel", callback_data="cancel_withdraw_all")
        ]
    ]
    update.message.reply_text(
        f"Are you sure you want to withdraw all SOL and SPL tokens to:
<code>{dest}</code>?",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

def handle_withdraw_all_confirmation(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    user_id = query.message.chat_id
    action = query.data

    if action == "cancel_withdraw_all":
        query.edit_message_text("❌ Withdrawal cancelled.")
        return

    if action == "confirm_withdraw_all":
        dest = WITHDRAW_STATE.get(user_id)
        if not dest:
            query.edit_message_text("❌ No destination found.")
            return

        try:
            kp = load_wallet_from_env()
            source_pub = kp.public_key
            dest_pub = PublicKey(dest)

            tx = Transaction()

            # Transfer SOL
            sol_balance = client.get_balance(source_pub)["result"]["value"]
            if sol_balance > 5000:
                lamports_to_send = sol_balance - 5000
                tx.add(
                    transfer(
                        TransferParams(
                            from_pubkey=source_pub,
                            to_pubkey=dest_pub,
                            lamports=lamports_to_send
                        )
                    )
                )

            # Transfer SPL Tokens
            for symbol, token in SPL_TOKENS.items():
                mint = token["mint"]
                decimals = token["decimals"]
                ata_src = get_associated_token_address(source_pub, mint)
                ata_dst = get_associated_token_address(dest_pub, mint)
                balance = client.get_token_account_balance(ata_src)["result"]["value"]
                amount = float(balance["uiAmount"])
                if amount > 0:
                    ui_amount = int(amount * (10 ** decimals))
                    tx.add(
                        transfer_checked(
                            program_id=TOKEN_PROGRAM_ID,
                            source=ata_src,
                            mint=mint,
                            dest=ata_dst,
                            owner=source_pub,
                            amount=ui_amount,
                            decimals=decimals
                        )
                    )

            if not tx.instructions:
                query.edit_message_text("⚠️ No funds to withdraw.")
                return

            sig = client.send_transaction(tx, kp)["result"]
            query.edit_message_text(
                f"✅ Withdrawal complete.
🔗 <a href='https://solscan.io/tx/{sig}'>View Transaction</a>",
                parse_mode="HTML"
            )
        except Exception as e:
            query.edit_message_text(f"❌ Error: {e}")

# Handlers
withdraw_all_handler = CommandHandler("withdrawall", withdraw_all)
confirm_all_handler = CallbackQueryHandler(handle_withdraw_all_confirmation, pattern="^confirm_withdraw_all|cancel_withdraw_all$")
