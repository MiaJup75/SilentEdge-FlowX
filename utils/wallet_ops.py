import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, CommandHandler, CallbackQueryHandler
from solana.publickey import PublicKey
from utils.wallet import get_wallet_address, get_wallet_balance, transfer_all_tokens_and_sol

# In-memory state for pending withdrawals
WITHDRAW_ALL_STATE = {}

# === /withdrawall Handler ===
def withdrawall(update: Update, context: CallbackContext):
    if not context.args:
        update.message.reply_text("❌ Usage: /withdrawall <destination_wallet_address>")
        return

    dest = context.args[0]
    if not dest or len(dest) < 32:
        update.message.reply_text("❌ Invalid wallet address.")
        return

    chat_id = update.effective_chat.id
    WITHDRAW_ALL_STATE[chat_id] = dest

    buttons = [
        [
            InlineKeyboardButton("✅ Confirm", callback_data="confirm_all_withdraw"),
            InlineKeyboardButton("❌ Cancel", callback_data="cancel_all_withdraw")
        ]
    ]

    update.message.reply_text(
        f"Are you sure you want to withdraw all SOL and SPL tokens to:\n<code>{dest}</code>?",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# === Callback for Confirmation ===
def handle_withdrawall_confirmation(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    chat_id = query.message.chat_id
    action = query.data

    if action == "cancel_all_withdraw":
        query.edit_message_text("❌ Withdraw cancelled.")
        return

    if action == "confirm_all_withdraw":
        dest = WITHDRAW_ALL_STATE.get(chat_id)
        if not dest:
            query.edit_message_text("❌ No destination found.")
            return

        try:
            user_pubkey = get_wallet_address()
            tx_links = transfer_all_tokens_and_sol(user_pubkey, dest)

            if not tx_links:
                query.edit_message_text("⚠️ No tokens to transfer or all failed.")
                return

            msg = "✅ Withdraw complete:\n"
            for symbol, link in tx_links.items():
                msg += f"• {symbol}: <a href='{link}'>View Tx</a>\n"

            query.edit_message_text(msg, parse_mode="HTML")

        except Exception as e:
            query.edit_message_text(f"❌ Error: {e}")

# === Handlers ===
withdraw_all_handler = CommandHandler("withdrawall", withdrawall)
confirm_all_handler = CallbackQueryHandler(handle_withdrawall_confirmation, pattern="^confirm_all_withdraw|cancel_all_withdraw$")
