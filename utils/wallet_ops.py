# utils/wallet_ops.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

from utils.wallet import get_wallet_address, get_wallet_balance, transfer_all_tokens_and_sol
from config import OWNER_ID


def withdrawall(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if user_id != OWNER_ID:
        update.message.reply_text("⛔ This command is restricted.")
        return

    if not context.args:
        update.message.reply_text("❗ Usage: /withdrawall <recipient_wallet_address>")
        return

    recipient = context.args[0]

    keyboard = [
        [
            InlineKeyboardButton("✅ Confirm", callback_data=f"confirm_all_withdraw:{recipient}"),
            InlineKeyboardButton("❌ Cancel", callback_data="cancel_all_withdraw")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text(
        f"⚠️ Are you sure you want to withdraw all SOL and SPL tokens to:\n\n<code>{recipient}</code>\n\nConfirm?",
        parse_mode="HTML",
        reply_markup=reply_markup
    )


def handle_withdrawall_confirmation(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = update.effective_user.id
    query.answer()

    if user_id != OWNER_ID:
        query.edit_message_text("⛔ Action not permitted.")
        return

    if query.data.startswith("confirm_all_withdraw:"):
        recipient = query.data.split(":")[1]

        try:
            query.edit_message_text("⏳ Processing withdrawal...")

            result = transfer_all_tokens_and_sol(recipient)

            query.edit_message_text(
                f"✅ Withdrawal Complete.\n\n<code>{result}</code>",
                parse_mode="HTML"
            )
        except Exception as e:
            query.edit_message_text(
                f"❌ Withdrawal Failed:\n<code>{e}</code>",
                parse_mode="HTML"
            )
    elif query.data == "cancel_all_withdraw":
        query.edit_message_text("❌ Withdrawal Cancelled.")
