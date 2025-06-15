import os

PIN_ENABLED = os.getenv("PIN_WELCOME_ENABLED", "true").lower() == "true"

def pin_welcome_message(bot, chat_id):
    if not PIN_ENABLED:
        return

    try:
        chat = bot.get_chat(chat_id)
        pinned = chat.pinned_message

        if pinned:
            return  # Already pinned

        msg = bot.send_message(chat_id, "📌 Flow X is live. Use /menu to begin.")
        bot.pin_chat_message(chat_id=chat_id, message_id=msg.message_id)
    except Exception as e:
        print(f"⚠️ Pinning error: {e}")
