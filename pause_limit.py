from telegram import Update
from telegram.ext import CallbackContext
from state_manager import is_paused, set_pause, set_limit
from config import OWNER_ID

# === /pause Command ===
def pause(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if OWNER_ID and user_id != OWNER_ID:
        update.message.reply_text("⛔ Access denied.")
        return

    current = is_paused()
    set_pause(not current)

    update.message.reply_text(
        "⏸ Trading paused." if not current else "▶️ Trading resumed."
    )

# === /limit Command ===
def limit(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if OWNER_ID and user_id != OWNER_ID:
        update.message.reply_text("⛔ Access denied.")
        return

    if not context.args:
        update.message.reply_text("🧮 Usage: /limit <number>")
        return

    try:
        limit_value = int(context.args[0])
        set_limit(limit_value)
        update.message.reply_text(f"📉 Daily trade limit set to {limit_value}")
    except ValueError:
        update.message.reply_text("⚠️ Please enter a valid number.")
