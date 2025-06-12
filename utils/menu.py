from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def get_main_menu():
    return InlineKeyboardMarkup([
        # Trading Actions
        [
            InlineKeyboardButton("💰 Buy", callback_data="buy"),
            InlineKeyboardButton("📤 Sell", callback_data="sell")
        ],
        [
            InlineKeyboardButton("📊 Balance", callback_data="balance"),
            InlineKeyboardButton("🔄 Ping", callback_data="ping")
        ],
        [
            InlineKeyboardButton("📘 Help", callback_data="help"),
            InlineKeyboardButton("🧭 Menu", callback_data="menu")
        ],

        # Utility Bots
        [
            InlineKeyboardButton("🤖 ChainBot", callback_data="link:ChainBot"),
            InlineKeyboardButton("📈 FXBot", callback_data="link:FXBot"),
            InlineKeyboardButton("📊 EquitiesBot", callback_data="link:EquitiesBot")
        ],

        # Future Controls (Disabled by default)
        [
            InlineKeyboardButton("⏸ Pause Bot", callback_data="pause"),  # Not active yet
            InlineKeyboardButton("⚠️ Set Limit", callback_data="limit")  # Not active yet
        ]
    ])
