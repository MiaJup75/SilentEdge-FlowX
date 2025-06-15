# pause_limit.py

from telegram import Update
from telegram.ext import CallbackContext
from config import OWNER_ID
from state_manager import is_paused, set_pause, set_limit

# === /pause Command ===
def pause(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if OWNER_ID and user_id != OWNER_ID:
        update.message.reply_text("⛔ Access denied.")
        return

    currently_paused = is_paused()
    set_pause(not currently_paused)

    update.message.reply_text(
        "⏸ Trading paused." if not currently_paused else "▶️ Trading resumed."
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
        daily_limit = int(context.args[0])
        set_limit(daily_limit)
        update.message.reply_text(f"📉 Daily trade limit set to {daily_limit}")
    except ValueError:
        update.message.reply_text("⚠️ Please enter a valid number.")
