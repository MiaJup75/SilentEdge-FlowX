import os
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, CommandHandler, CallbackQueryHandler
from solana.rpc.api import Client
from solana.transaction import Transaction
from solana.publickey import PublicKey
from solana.system_program import TransferParams, transfer
from utils.signer import load_wallet_from_env

# === Withdraw Handler ===
WITHDRAW_STATE = {}
SOLANA_RPC = os.getenv("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com")
client = Client(SOLANA_RPC)


def withdraw(update: Update, context: CallbackContext):
    if not context.args:
        update.message.reply_text("❌ Usage: /withdraw <destination_wallet_address>")
        return

    dest = context.args[0]
    if not dest or len(dest) < 32:
        update.message.reply_text("❌ Invalid wallet address.")
        return

    WITHDRAW_STATE[update.effective_chat.id] = dest
    buttons = [
        [
            InlineKeyboardButton("✅ Confirm", callback_data="confirm_withdraw"),
            InlineKeyboardButton("❌ Cancel", callback_data="cancel_withdraw")
        ]
    ]
    update.message.reply_text(
        f"Are you sure you want to withdraw ALL SOL to:
<code>{dest}</code>?",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


def handle_withdraw_confirmation(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    user_id = query.message.chat_id
    action = query.data

    if action == "cancel_withdraw":
        query.edit_message_text("❌ Withdraw cancelled.")
        return

    if action == "confirm_withdraw":
        dest = WITHDRAW_STATE.get(user_id)
        if not dest:
            query.edit_message_text("❌ No destination found.")
            return

        try:
            kp = load_wallet_from_env()
            source_pub = kp.public_key
            dest_pub = PublicKey(dest)

            # Get current balance
            sol_balance = client.get_balance(source_pub)["result"]["value"]
            if sol_balance < 5000:
                query.edit_message_text("⚠️ Not enough SOL to cover fees.")
                return

            lamports_to_send = sol_balance - 5000  # Leave buffer for fees

            tx = Transaction()
            tx.add(
                transfer(
                    TransferParams(
                        from_pubkey=source_pub,
                        to_pubkey=dest_pub,
                        lamports=lamports_to_send
                    )
                )
            )
            tx_sig = client.send_transaction(tx, kp)["result"]
            query.edit_message_text(
                f"✅ Sent {lamports_to_send / 1e9:.5f} SOL to <code>{dest}</code>\n"
                f"🔗 <a href='https://solscan.io/tx/{tx_sig}'>View on Solscan</a>",
                parse_mode="HTML"
            )
        except Exception as e:
            query.edit_message_text(f"❌ Error: {e}")


# === Register with dispatcher (add these to your bot setup) ===
withdraw_handler = CommandHandler("withdraw", withdraw)
confirm_handler = CallbackQueryHandler(handle_withdraw_confirmation, pattern="^confirm_withdraw|cancel_withdraw$")
dispatcher.add_handler(withdraw_handler)
dispatcher.add_handler(confirm_handler)
