# === handlers/pnl_handlers.py ===
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import CallbackContext
from utils.pnl import calculate_daily_pnl
from utils.charts import generate_pnl_chart

def pnl(update: Update, context: CallbackContext):
    query_arg = context.args[0].lower() if context.args else "today"
    data, summary = calculate_daily_pnl(query_arg)

    # Inline buttons
    keyboard = [
        [
            InlineKeyboardButton("📅 Today", callback_data="pnl_today"),
            InlineKeyboardButton("📆 Yesterday", callback_data="pnl_yesterday"),
            InlineKeyboardButton("📊 All Time", callback_data="pnl_alltime"),
        ]
    ]

    # Chart
    chart_path = generate_pnl_chart(data, period=query_arg)
    with open(chart_path, "rb") as chart:
        update.message.reply_photo(
            photo=chart,
            caption=summary,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.HTML
        )

def handle_pnl_button(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    period = query.data.replace("pnl_", "")
    data, summary = calculate_daily_pnl(period)

    keyboard = [
        [
            InlineKeyboardButton("📅 Today", callback_data="pnl_today"),
            InlineKeyboardButton("📆 Yesterday", callback_data="pnl_yesterday"),
            InlineKeyboardButton("📊 All Time", callback_data="pnl_alltime"),
        ]
    ]

    chart_path = generate_pnl_chart(data, period=period)
    with open(chart_path, "rb") as chart:
        query.message.reply_photo(
            photo=chart,
            caption=summary,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.HTML
        )
