from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def get_main_menu(is_live=False, trade_limit=5):
    # Label for mode
    mode_label = "✅ LIVE MODE" if is_live else "🧪 SIM MODE"
    limit_label = f"${trade_limit:.2f} Limit"

    return InlineKeyboardMarkup([
        # Status Display Row
        [
            InlineKeyboardButton(mode_label, callback_data="noop"),
            InlineKeyboardButton(limit_label, callback_data="noop")
        ],

        # Trading Actions
        [
            InlineKeyboardButton("💰 Buy", callback_data="buy"),
            InlineKeyboardButton("📤 Sell", callback_data="sell")
        ],
        [
            InlineKeyboardButton("📊 Balance", callback_data="balance"),
            InlineKeyboardButton("🧠 Ask AI", callback_data="aiprompt")
        ],
        [
            InlineKeyboardButton("📘 Help", callback_data="help"),
            InlineKeyboardButton("🔄 Ping", callback_data="ping")
        ],

        # Menu Refresh
        [
            InlineKeyboardButton("🧭 Refresh Menu", callback_data="menu")
        ],

        # Future Controls (can be activated later)
        [
            InlineKeyboardButton("⏸ Pause Bot", callback_data="pause"),
            InlineKeyboardButton("⚠️ Set Limit", callback_data="limit")
        ],

        # Utility Bots
        [
            InlineKeyboardButton("🤖 ChainBot", callback_data="link:ChainBot"),
            InlineKeyboardButton("📈 FXBot", callback_data="link:FXBot"),
            InlineKeyboardButton("📊 EquitiesBot", callback_data="link:EquitiesBot")
        ]
    ])
