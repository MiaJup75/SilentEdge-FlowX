def pin_welcome_message(bot, chat_id):
    messages = bot.get_chat(chat_id).get_pinned_message()
    if messages:
        return  # Already pinned
    bot.send_message(chat_id, "📌 Flow X is live. Use /menu to begin.")
