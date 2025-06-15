# === handlers/menu.py ===
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from config import TRADE_AMOUNT

def get_main_menu(is_live=True, trade_limit=TRADE_AMOUNT, trades_today=0):
    mode_label = "✅ LIVE MODE" if is_live else "🧪 SIM MODE"
    limit_label = f"${trade_limit:.2f} Limit"
    trades_label = f"{trades_today} Trades Today"

    return InlineKeyboardMarkup([
        # ── Status Row ──
        [
            InlineKeyboardButton(mode_label, callback_data="noop"),
            InlineKeyboardButton(limit_label, callback_data="noop"),
            InlineKeyboardButton(trades_label, callback_data="noop")
        ],

        # ── Trading Row ──
        [
            InlineKeyboardButton("💰 Buy", callback_data="buy"),
            InlineKeyboardButton("📤 Sell", callback_data="sell")
        ],

        # ── Wallet & PnL Row ──
        [
            InlineKeyboardButton("📊 Balance", callback_data="balance"),
            InlineKeyboardButton("📈 PnL", callback_data="pnl")
        ],

        # ── Tools Row ──
        [
            InlineKeyboardButton("🧠 Ask AI", callback_data="aiprompt"),
            InlineKeyboardButton("📘 Help", callback_data="help")
        ],
        [
            InlineKeyboardButton("🔄 Ping", callback_data="ping"),
            InlineKeyboardButton("🧭 Refresh", callback_data="menu")
        ],

        # ── Controls Row ──
        [
            InlineKeyboardButton("⏸ Pause Bot", callback_data="pause"),
            InlineKeyboardButton("⚠️ Set Limit", callback_data="limit")
        ],

        # ── Other Bots Row ──
        [
            InlineKeyboardButton("🤖 ChainBot", callback_data="link:ChainBot"),
            InlineKeyboardButton("📈 FXBot", callback_data="link:FXBot"),
            InlineKeyboardButton("📊 EquitiesBot", callback_data="link:EquitiesBot")
        ]
    ])
