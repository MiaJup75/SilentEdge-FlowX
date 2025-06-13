import os
import logging
import traceback

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, Message, InputMediaPhoto
)
from telegram.ext import (
    Updater, CommandHandler, CallbackQueryHandler,
    MessageHandler, Filters, CallbackContext
)

from utils.wallet import get_wallet_address
from utils.trade import execute_jupiter_trade
from utils.pnl import calculate_daily_pnl
from utils.format import (
    format_trade_result,
    format_balance_text,
    format_error_message,
    format_help_text,
    format_debug_info
)
from utils.format import format_pnl_summary
from utils.ping import check_jupiter_health
from utils.gpt import ask_chatgpt
from utils.reporting import send_daily_pnl_summary
from utils.charts import generate_pnl_chart
from utils.format import format_pnl_summary
from utils.menu import get_main_menu
from handlers.pnl_handlers import pnl, handle_pnl_button
from utils.pin import pin_welcome_message
from state_manager import (
    is_paused,
    check_and_increment_trade_count,
    reset_trade_count,
    set_pause,
    set_limit
)

# === Logger ===
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# === Environment Setup ===
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TRADE_AMOUNT_USDC = float(os.getenv("TRADE_AMOUNT_USDC", "5"))
LIVE_MODE = os.getenv("LIVE_MODE", "false").lower() == "true"
OWNER_ID = int(os.getenv("OWNER_ID", "0"))

# === Load Wallet ===
wallet_address = "8xfd61QP7PA2zkeazJvTCYCwLj9eMqodZ1uUW19SEoL6"
wallet = wallet_address  # compatibility alias

# === Bot State Flags ===
bot_paused = False
daily_trade_limit = 20
trades_today = 0

try:
    balance = get_wallet_balance(wallet_address)
    print("🧠 Wallet Address:", wallet_address)
    print("💰 Wallet Balance:", balance)
except Exception as e:
    logger.warning(f"Could not fetch balance: {e}")
    balance = {}

# === Start Command ===
def start(update: Update, context: CallbackContext):
    user = update.effective_user
    chat_id = update.effective_chat.id
    logger.info(f"/start used by {user.username or user.id}")

    welcome = (
        "🚀 <b>Welcome to Flow X Bot</b>\n\n"
        f"<b>Wallet:</b> <code>{wallet_address}</code>\n"
        f"<b>Mode:</b> {'✅ <b>LIVE</b>' if LIVE_MODE else '🧪 <b>SIMULATED</b>'}\n"
        f"<b>Trade Size:</b> ${TRADE_AMOUNT_USDC:.2f}\n\n"
        "Tap a button or type a command to begin. ⬇️"
    )

    context.bot.send_message(
        chat_id=chat_id,
        text=welcome,
        parse_mode=ParseMode.HTML
    )

    # Pin the welcome message
    try:
        pin_welcome_message(context.bot, chat_id)
    except Exception as e:
        logger.warning(f"Could not pin message: {e}")
        # === Button Handler ===
def button(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = update.effective_user.id
    action = query.data
    query.answer()

    logger.info(f"Button '{action}' used by {user_id}")

    try:
        if action in ["buy", "sell"]:
            query.edit_message_text("⏳ Executing trade...")
            result = execute_jupiter_trade(wallet, action.upper(), TRADE_AMOUNT_USDC, LIVE_MODE)
            query.edit_message_text(
                text=format_trade_result(result),
                parse_mode=ParseMode.HTML
            )

        elif action == "balance":
            query.edit_message_text("⏳ Fetching balance...")
            balances, balance_text = get_wallet_balance(get_wallet_address(wallet))
            query.edit_message_text(
                text=balance_text,
                parse_mode=ParseMode.HTML
            )

        elif data == "pnl":
            _, message = calculate_daily_pnl("today")
            query.edit_message_text(
                message,
                parse_mode=ParseMode.HTML
            )

        elif action == "help":
            query.edit_message_text(
                text=format_help_text(),
                parse_mode=ParseMode.HTML
            )

        elif action == "ping":
            query.edit_message_text(
                text=check_jupiter_health(),
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
                    reply_markup=InlineKeyboardMarkup([
                        [
                            InlineKeyboardButton("📅 Today", callback_data="pnl:today"),
                            InlineKeyboardButton("🕘 Yesterday", callback_data="pnl:yesterday"),
                            InlineKeyboardButton("📊 All Time", callback_data="pnl:alltime")
                        ]
                    ])
                )

        elif action == "menu":
            query.edit_message_text(
                text="📋 Main Menu:",
                reply_markup=get_main_menu(is_live=LIVE_MODE, trade_limit=TRADE_AMOUNT_USDC),
                parse_mode=ParseMode.HTML
            )

        elif action.startswith("link:"):
            label = action.split(":")[1]
            query.edit_message_text(
                text=f"🔗 Redirecting to {label} bot..."
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
def buy(update: Update, context: CallbackContext):
    try:
        # === Trade Guard ===
        if is_paused():
            update.message.reply_text("⛔ Trading is currently paused.")
            return
        if not check_and_increment_trade_count():
            update.message.reply_text("⚠️ Daily trade limit reached.")
            return

        update.message.reply_text("⏳ Executing buy trade...")
        result = execute_jupiter_trade(wallet, "BUY", TRADE_AMOUNT_USDC, LIVE_MODE)
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

def sell(update: Update, context: CallbackContext):
    try:
        # === Trade Guard ===
        if is_paused():
            update.message.reply_text("⛔ Trading is currently paused.")
            return
        if not check_and_increment_trade_count():
            update.message.reply_text("⚠️ Daily trade limit reached.")
            return

        update.message.reply_text("⏳ Executing sell trade...")
        result = execute_jupiter_trade(wallet, "SELL", TRADE_AMOUNT_USDC, LIVE_MODE)
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

# === /balance Command ===
def balance(update: Update, context: CallbackContext):
    try:
        update.message.reply_text("⏳ Fetching balance...")
        balances, balance_text = get_wallet_balance(wallet_address)
        update.message.reply_text(
            balance_text,
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        logger.error(f"/balance error: {e}")
        update.message.reply_text(
            format_error_message(f"❌ Format Error\n<code>{e}</code>"),
            parse_mode=ParseMode.HTML
        )

# === /ping Command ===
def ping(update: Update, context: CallbackContext):
    try:
        update.message.reply_text("⏳ Checking Jupiter status...")
        ping_text = check_jupiter_health()
        update.message.reply_text(
            ping_text,
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        logger.error(f"/ping error: {e}")
        update.message.reply_text(
            format_error_message("❌ Ping check failed."),
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
        debug_text = format_debug_info(get_wallet_address(wallet), LIVE_MODE, TRADE_AMOUNT_USDC)
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

        # Get live state data
        from state_manager import load_state
        state = load_state()
        trades_today = state.get("trades_today", 0)

        update.message.reply_text(
            "📋 Main Menu:",
            reply_markup=get_main_menu(
                is_live=LIVE_MODE,
                trade_limit=TRADE_AMOUNT_USDC,
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
        arg = context.args[0].lower() if context.args else "today"
        if arg not in ["today", "yesterday", "alltime"]:
            update.message.reply_text("❗ Use /pnl [today|yesterday|alltime]")
            return

        update.message.reply_text("⏳ Fetching PnL...")

        report = calculate_daily_pnl(arg)
        summary = format_pnl_summary(report)

        # Generate chart image
        chart_path = generate_pnl_chart(report["history"], arg)

        # Send image + summary
        with open(chart_path, "rb") as img:
            update.message.reply_photo(
                photo=img,
                caption=summary,
                parse_mode=ParseMode.HTML,
                reply_markup=InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton("📅 Today", callback_data="pnl:today"),
                        InlineKeyboardButton("🕘 Yesterday", callback_data="pnl:yesterday"),
                        InlineKeyboardButton("📊 All Time", callback_data="pnl:alltime")
                    ]
                ])
            )

    except Exception as e:
        logger.error(f"/pnl error: {e}")
        update.message.reply_text(
            format_error_message("❌ Failed to generate PnL."),
            parse_mode=ParseMode.HTML
        )

    except Exception as e:
        logger.error(f"/pnl error: {e}")
        update.message.reply_text(
            format_error_message("❌ Failed to generate PnL."),
            parse_mode=ParseMode.HTML
        )

# === /aiprompt Command ===
def aiprompt(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if OWNER_ID and user_id != OWNER_ID:
        update.message.reply_text("⛔ Access denied.")
        return

    prompt = ' '.join(context.args)
    if not prompt:
        update.message.reply_text("💬 Please enter a prompt after /aiprompt.")
        return

    try:
        update.message.reply_text("⏳ Asking ChatGPT...")
        response = ask_chatgpt(prompt)
        update.message.reply_text(
            f"🤖 <b>ChatGPT:</b>\n{response}",
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        logger.error(f"/aiprompt error: {e}")
        update.message.reply_text(
            format_error_message("❌ ChatGPT failed."),
            parse_mode=ParseMode.HTML
        )

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

# === Bot Launcher ===
def main():
    if not TELEGRAM_TOKEN:
        logger.error("❌ TELEGRAM_TOKEN missing. Cannot start bot.")
        return

    logger.info("🚀 Starting Flow X Bot...")
    updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Register slash commands for Telegram interface
    updater.bot.set_my_commands([
        ("start", "Launch bot"),
        ("buy", "Simulate Buy"),
        ("sell", "Simulate Sell"),
        ("balance", "Wallet Balance"),
        ("pnl", "PnL Summary"),
        ("ping", "Jupiter Check"),
        ("help", "Help Menu"),
        ("debug", "Bot Status"),
        ("menu", "Show Buttons"),
        ("aiprompt", "Ask ChatGPT")
    ])

    PORT = int(os.environ.get("PORT", "10000"))
    WEBHOOK_URL = os.environ.get("WEBHOOK_URL")

    updater.start_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TELEGRAM_TOKEN,
        webhook_url=f"{WEBHOOK_URL}/{TELEGRAM_TOKEN}"
    )
           # Register command handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("buy", buy))
    dispatcher.add_handler(CommandHandler("sell", sell))
    dispatcher.add_handler(CommandHandler("balance", balance))
    dispatcher.add_handler(CommandHandler("pnl", pnl))
    dispatcher.add_handler(CommandHandler("ping", ping))
    dispatcher.add_handler(CommandHandler("help", help_cmd))
    dispatcher.add_handler(CommandHandler("debug", debug))
    dispatcher.add_handler(CommandHandler("menu", menu))
    dispatcher.add_handler(CommandHandler("aiprompt", aiprompt))
    dispatcher.add_handler(CommandHandler("pause", pause))
    dispatcher.add_handler(CommandHandler("limit", limit))
    dispatcher.add_handler(CommandHandler("pnl", pnl))
    dispatcher.add_handler(CallbackQueryHandler(handle_pnl_button, pattern="^pnl_"))

    # Handle inline button callbacks
    dispatcher.add_handler(CallbackQueryHandler(button))

    # Catch-all for non-command messages
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, fallback_message))

# === Scheduler: Daily 9AM Report ===
job_queue.run_daily(
    send_daily_pnl_summary,
    time=datetime.time(hour=9, minute=0, tzinfo=bkk_tz)
)
import os
import pytz
import datetime
from telegram.ext import Updater, CallbackContext
from telegram import Update, ParseMode
from utils.reporting import send_daily_pnl_summary
import logging

# Load bot token
TOKEN = os.getenv("BOT_TOKEN")  # Or: from config import TOKEN

# Set timezone
bkk_tz = pytz.timezone("Asia/Bangkok")

# === Fallback Text Response ===
def fallback_message(update: Update, context: CallbackContext):
    update.message.reply_text(
        "🤖 I didn’t understand that. Use /menu to get started.",
        parse_mode=ParseMode.HTML
    )

# === Bot Startup ===
if __name__ == '__main__':
    main()
