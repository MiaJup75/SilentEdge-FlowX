from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def get_main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💰 Buy", callback_data="buy")],
        [InlineKeyboardButton("📤 Sell", callback_data="sell")],
        [InlineKeyboardButton("📊 Balance", callback_data="balance")],
        [InlineKeyboardButton("📘 Help", callback_data="help")],
        [InlineKeyboardButton("🔄 Ping", callback_data="ping")],
        [InlineKeyboardButton("🧭 Menu", callback_data="menu")],
        [InlineKeyboardButton("🤖 ChainBot", callback_data="link:ChainBot")],
        [InlineKeyboardButton("📈 FXBot", callback_data="link:FXBot")],
        [InlineKeyboardButton("📊 EquitiesBot", callback_data="link:EquitiesBot")]
    ])
