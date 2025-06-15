import os
import logging
import traceback
import sys

sys.stdout.reconfigure(line_buffering=True)

from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, Message, InputMediaPhoto
)
from telegram.ext import (
    Updater, CommandHandler, CallbackQueryHandler,
    MessageHandler, Filters, CallbackContext
)

from utils.binance_trade import execute_binance_trade
from utils.pnl import calculate_daily_pnl, calculate_auto_pnl
from utils.format import (
    format_trade_result,
    format_error_message,
    format_help_text,
    format_debug_info,
    format_pnl_summary,
    get_pnl_buttons
)
from utils.reporting import send_daily_pnl_chart
from utils.charts import generate_pnl_chart
from utils.menu import get_main_menu
from handlers.pnl_handlers import pnl, handle_pnl_button
from utils.pin import pin_welcome_message
from utils.telegram_alerts import send_alert
from state_manager import (
    is_paused,
    check_and_increment_trade_count,
    reset_trade_count,
    set_pause,
    set_limit
)

# === /reboot Command ===
def reboot(update, context):
    user_id = str(update.effective_user.id)
    if user_id == os.getenv("TELEGRAM_USER_ID"):
        update.message.reply_text("♻️ Rebooting bot... (manual action may be required on Render)")
    else:
        update.message.reply_text("🚫 You are not authorized to reboot the bot.")

# === Logger Setup ===
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

logger.info("✅ TP/SL watcher thread started.")

from config import TRADE_AMOUNT, OWNER_ID, TELEGRAM_TOKEN, LIVE_MODE, PORT, WEBHOOK_URL, SLIPPAGE_TOLERANCE, BASE_TOKEN, QUOTE_TOKEN

# === Debug Output ===
print("🛠 Flow X Config Debug:")
print("→ BASE:", BASE_TOKEN)
print("→ QUOTE:", QUOTE_TOKEN)
print("→ TRADE_AMOUNT:", TRADE_AMOUNT)
print("→ SLIPPAGE:", SLIPPAGE_TOLERANCE)
print("→ LIVE_MODE:", LIVE_MODE)

# === Bot State ===
bot_paused = False
daily_trade_limit = 20
trades_today = 0

# === /start Command ===
def start(update: Update, context: CallbackContext):
    user = update.effective_user
    chat_id = update.effective_chat.id
    logger.info(f"/start used by {user.username or user.id}")

    welcome = (
        "🚀 <b>Welcome to Flow X Bot</b>\n\n"
        f"<b>Mode:</b> ✅ <b>LIVE</b>\n"
        f"<b>Trade Size:</b> ${TRADE_AMOUNT:.2f}\n\n"
        "Tap a button or type a command to begin. ⬇️"
    )

    context.bot.send_message(
        chat_id=chat_id,
        text=welcome,
        parse_mode=ParseMode.HTML
    )

    try:
        pin_welcome_message(context.bot, chat_id)
    except Exception as e:
        logger.warning(f"Could not pin message: {e}")

# === Inline Button Handler ===
def button(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = update.effective_user.id
    action = query.data
    query.answer()

    logger.info(f"Button '{action}' used by {user_id}")

    try:
        if action in ["buy", "sell"]:
            if is_paused():
                query.edit_message_text("⛔ Trading is currently paused.")
                return
            if not check_and_increment_trade_count():
                query.edit_message_text("⚠️ Daily trade limit reached.")
                return

            query.edit_message_text("⏳ Executing trade...")
            result = execute_binance_trade(
                side=action.upper(),
                amount_usdc=TRADE_AMOUNT,
                live=LIVE_MODE,
                slippage=SLIPPAGE_TOLERANCE
            )
            query.edit_message_text(
                text=format_trade_result(result),
                parse_mode=ParseMode.HTML
            )

        elif action == "pnl":
            report = calculate_auto_pnl()
            summary = format_pnl_summary(report)
            query.edit_message_text(
                summary,
                parse_mode=ParseMode.HTML
            )

        elif action == "help":
            query.edit_message_text(
                text=format_help_text(),
                parse_mode=ParseMode.HTML
            )

        elif action.startswith("pnl:"):
            view = action.split(":")[1]
            report = calculate_daily_pnl(view)
            summary = format_pnl_summary(report)
            chart_path = generate_pnl_chart(report["history"], view)

            with open(chart_path, "rb") as img:
                query.edit_message_media(
                    media=InputMediaPhoto(media=img, caption=summary, parse_mode=ParseMode.HTML),
                    reply_markup=get_pnl_buttons(view)
                )

        elif action == "menu":
            query.edit_message_text(
                text="📅 Main Menu:",
                reply_markup=get_main_menu(is_live=LIVE_MODE, trade_limit=TRADE_AMOUNT),
                parse_mode=ParseMode.HTML
            )

        else:
            query.edit_message_text(
                text="⚠️ Unknown action selected.",
                parse_mode=ParseMode.HTML
            )

    except Exception as e:
        logger.error(f"[button] {e}\n{traceback.format_exc()}")
        query.edit_message_text(
            text=format_error_message("❌ Something went wrong. Try again."),
            parse_mode=ParseMode.HTML
        )

# === /buy Command ===
def buy(update: Update, context: CallbackContext):
    try:
        if is_paused():
            update.message.reply_text("⛔ Trading is currently paused.")
            return
        if not check_and_increment_trade_count():
            update.message.reply_text("⚠️ Daily trade limit reached.")
            return

        update.message.reply_text("⏳ Executing buy trade...")
        result = execute_binance_trade(
            side="BUY",
            amount_usdc=TRADE_AMOUNT,
            live=LIVE_MODE,
            slippage=SLIPPAGE_TOLERANCE
        )
        update.message.reply_text(
            format_trade_result(result),
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        logger.error(f"/buy error: {e}")
        update.message.reply_text(
            format_error_message("❌ Buy failed."),
            parse_mode=ParseMode.HTML
        )

# === /sell Command ===
def sell(update: Update, context: CallbackContext):
    try:
        if is_paused():
            update.message.reply_text("⛔ Trading is currently paused.")
            return
        if not check_and_increment_trade_count():
            update.message.reply_text("⚠️ Daily trade limit reached.")
            return

        update.message.reply_text("⏳ Executing sell trade...")
        result = execute_binance_trade(
            side="SELL",
            amount_usdc=TRADE_AMOUNT,
            live=LIVE_MODE,
            slippage=SLIPPAGE_TOLERANCE
        )
        update.message.reply_text(
            format_trade_result(result),
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        logger.error(f"/sell error: {e}")
        update.message.reply_text(
            format_error_message("❌ Sell failed."),
            parse_mode=ParseMode.HTML
        )

# === /help Command ===
def help_cmd(update: Update, context: CallbackContext):
    try:
        update.message.reply_text("⏳ Loading help menu...")
        help_text = format_help_text()
        update.message.reply_text(
            help_text,
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        logger.error(f"/help error: {e}")
        update.message.reply_text(
            format_error_message("❌ Help unavailable."),
            parse_mode=ParseMode.HTML
        )

# === /debug Command ===
def debug(update: Update, context: CallbackContext):
    try:
        update.message.reply_text("⏳ Gathering debug info...")
        debug_text = format_debug_info("Binance", True, TRADE_AMOUNT)
        update.message.reply_text(
            debug_text,
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        logger.error(f"/debug error: {e}")
        update.message.reply_text(
            format_error_message("❌ Debug info failed."),
            parse_mode=ParseMode.HTML
        )

# === /menu Command ===
def menu(update: Update, context: CallbackContext):
    try:
        update.message.reply_text("⏳ Loading menu...")

        from state_manager import load_state
        state = load_state()
        trades_today = state.get("trades_today", 0)

        update.message.reply_text(
            "📋 Main Menu:",
            reply_markup=get_main_menu(
                is_live=LIVE_MODE,
                trade_limit=TRADE_AMOUNT,
                trades_today=trades_today
            ),
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        logger.error(f"/menu error: {e}")
        update.message.reply_text(
            format_error_message("⚠️ Menu load failed."),
            parse_mode=ParseMode.HTML
        )

# === /pnl Command ===
def pnl(update: Update, context: CallbackContext):
    try:
        arg = context.args[0].lower() if context.args else "auto"
        valid = ["today", "yesterday", "7d", "30d", "alltime"]
        if arg not in valid:
            update.message.reply_text("❗ Use /pnl [today|yesterday|7d|30d|alltime]")
            return
        day = arg

        report = calculate_auto_pnl() if day == "auto" else calculate_daily_pnl(day)
        summary = format_pnl_summary(report)
        chart_path = generate_pnl_chart(report["history"], label=day)

        if os.path.exists(chart_path):
            with open(chart_path, "rb") as img:
                update.message.reply_photo(
                    photo=img,
                    caption=summary,
                    parse_mode=ParseMode.HTML,
                    reply_markup=InlineKeyboardMarkup([
                        [
                            InlineKeyboardButton("📅 Today", callback_data="pnl:today"),
                            InlineKeyboardButton("📆 Yesterday", callback_data="pnl:yesterday"),
                            InlineKeyboardButton("7️⃣ 7D", callback_data="pnl:7d"),
                            InlineKeyboardButton("📊 30D", callback_data="pnl:30d"),
                            InlineKeyboardButton("🗓 All Time", callback_data="pnl:alltime")
                        ]
                    ])
                )
        else:
            update.message.reply_text(
                summary,
                parse_mode=ParseMode.HTML
            )

    except Exception as e:
        logger.error(f"/pnl error: {e}")
        update.message.reply_text(
            format_error_message("❌ Failed to generate PnL."),
            parse_mode=ParseMode.HTML
        )

# === /pause Command ===
def pause(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if OWNER_ID and user_id != OWNER_ID:
        update.message.reply_text("⛔ Access denied.")
        return

    current = is_paused()
    set_pause(not current)
    update.message.reply_text(
        f"{'⏸️ Trading paused.' if not current else '▶️ Trading resumed.'}"
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

# === Timezone Setup ===
import pytz
import datetime
bkk_tz = pytz.timezone("Asia/Bangkok")

# === Fallback Text ===
def fallback_message(update: Update, context: CallbackContext):
    update.message.reply_text(
        "🤖 I didn’t understand that. Use /menu to get started.",
        parse_mode=ParseMode.HTML
    )

# === Bot Launcher ===
def main():
    if not TELEGRAM_TOKEN:
        logger.error("❌ TELEGRAM_TOKEN missing. Cannot start bot.")
        return

    logger.info("🚀 Starting Flow X Bot...")
    updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    job_queue = updater.job_queue

    # === Start TP/SL Watcher in Background ===
    from utils.tp_sl_watcher import monitor_trades
    import threading
    threading.Thread(target=monitor_trades, daemon=True).start()

    # === Start Keep-Alive Server (optional) ===
    from keep_alive import run as keep_alive_server
    threading.Thread(target=keep_alive_server).start()

    # === Webhook Launch ===
    updater.start_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TELEGRAM_TOKEN,
        webhook_url=f"{WEBHOOK_URL}/{TELEGRAM_TOKEN}"
    )

    # === Register Slash Commands ===
    updater.bot.set_my_commands([
        ("start", "Launch bot"),
        ("buy", "Execute Buy Trade"),
        ("sell", "Execute Sell Trade"),
        ("pnl", "PnL Summary"),
        ("menu", "Show Buttons"),
        ("debug", "Bot Status"),
        ("help", "Help Menu"),
        ("pause", "Pause/Resume Trading"),
        ("limit", "Set Daily Trade Limit"),
        ("reboot", "Restart Bot")
    ])

    # === Register Handlers ===
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("buy", buy))
    dispatcher.add_handler(CommandHandler("sell", sell))
    dispatcher.add_handler(CommandHandler("pnl", pnl))
    dispatcher.add_handler(CommandHandler("menu", menu))
    dispatcher.add_handler(CommandHandler("debug", debug))
    dispatcher.add_handler(CommandHandler("help", help_cmd))
    dispatcher.add_handler(CommandHandler("pause", pause))
    dispatcher.add_handler(CommandHandler("limit", limit))
    dispatcher.add_handler(CommandHandler("reboot", reboot))

    # === Register Dynamic Symbol PnL Commands ===
    def generate_pnl_handler(symbol):
        def handler(update, context):
            result = calculate_daily_pnl("7d", symbol=symbol.upper())
            update.message.reply_text(result)
        return handler

    for coin in ["BTC", "ETH", "SOL", "XRP"]:
        dispatcher.add_handler(CommandHandler(f"pnl{coin.lower()}", generate_pnl_handler(coin)))

    # === Register Callback and Fallback ===
    dispatcher.add_handler(CallbackQueryHandler(handle_pnl_button, pattern="^pnl:"))
    dispatcher.add_handler(CallbackQueryHandler(button))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, fallback_message))

    # === Schedule Daily PnL Chart Job (9AM BKK) ===
    job_queue.run_daily(
        send_daily_pnl_chart,
        time=datetime.time(hour=9, minute=0, tzinfo=bkk_tz)
    )

    # === Keep the Bot Alive ===
    updater.idle()

# === Entry Point ===
if __name__ == '__main__':
    main()
