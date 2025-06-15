import os
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, CommandHandler, CallbackQueryHandler
from solana.rpc.api import Client
from solana.transaction import Transaction
from solana.publickey import PublicKey
from solana.system_program import TransferParams, transfer
from spl.token.instructions import transfer_checked, get_associated_token_address
from utils.signer import load_wallet_from_env

# === State & Config ===
WITHDRAW_STATE = {}
SOLANA_RPC = os.getenv("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com")
client = Client(SOLANA_RPC)

# === Token Mints ===
SPL_TOKENS = {
    "USDC": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
    "wSOL": "So11111111111111111111111111111111111111112",
}

def withdrawall(update: Update, context: CallbackContext):
    if not context.args:
        update.message.reply_text("❌ Usage: /withdrawall <destination_wallet_address>")
        return

    dest = context.args[0]
    if not dest or len(dest) < 32:
        update.message.reply_text("❌ Invalid wallet address.")
        return

    WITHDRAW_STATE[update.effective_chat.id] = dest
    buttons = [[
        InlineKeyboardButton("✅ Confirm", callback_data="confirm_all_withdraw"),
        InlineKeyboardButton("❌ Cancel", callback_data="cancel_all_withdraw")
    ]]
    update.message.reply_text(
        f"Are you sure you want to withdraw all SOL and SPL tokens to: <code>{dest}</code>?",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

def handle_withdrawall_confirmation(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    user_id = query.message.chat_id
    action = query.data

    if action == "cancel_all_withdraw":
        query.edit_message_text("❌ Withdraw cancelled.")
        return

    if action == "confirm_all_withdraw":
        dest = WITHDRAW_STATE.get(user_id)
        if not dest:
            query.edit_message_text("❌ No destination wallet found.")
            return

        try:
            kp = load_wallet_from_env()
            source_pub = kp.public_key
            dest_pub = PublicKey(dest)

            # === Transfer SOL ===
            sol_balance = client.get_balance(source_pub)["result"]["value"]
            tx = Transaction()
            if sol_balance > 5000:
                tx.add(transfer(
                    TransferParams(
                        from_pubkey=source_pub,
                        to_pubkey=dest_pub,
                        lamports=sol_balance - 5000  # keep buffer
                    )
                ))

            # === Transfer SPL Tokens ===
            for symbol, mint in SPL_TOKENS.items():
                ata_src = get_associated_token_address(source_pub, PublicKey(mint))
                ata_dst = get_associated_token_address(dest_pub, PublicKey(mint))
                bal_resp = client.get_token_account_balance(ata_src)
                amount = float(bal_resp.get("result", {}).get("value", {}).get("uiAmount", 0))
                decimals = int(bal_resp.get("result", {}).get("value", {}).get("decimals", 6))
                if amount > 0:
                    tx.add(transfer_checked(
                        program_id=PublicKey("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"),
                        source=ata_src,
                        mint=PublicKey(mint),
                        dest=ata_dst,
                        owner=source_pub,
                        amount=int(amount * (10 ** decimals)),
                        decimals=decimals
                    ))

            if not tx.instructions:
                query.edit_message_text("⚠️ No tokens available to withdraw.")
                return

            sig = client.send_transaction(tx, kp)["result"]
            query.edit_message_text(
                f"✅ Withdrawal initiated to <code>{dest}</code>\n"
                f"🔗 <a href='https://solscan.io/tx/{sig}'>View on Solscan</a>",
                parse_mode="HTML"
            )
        except Exception as e:
            query.edit_message_text(f"❌ Error during withdrawal:\n<code>{e}</code>", parse_mode="HTML")
