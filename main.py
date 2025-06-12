import os
import logging
import traceback
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, Message
)
from telegram.ext import (
    Updater, CommandHandler, CallbackQueryHandler,
    MessageHandler, Filters, CallbackContext
)

from utils.wallet import load_wallet, get_wallet_address
from utils.trade import execute_jupiter_trade
from utils.balance import get_wallet_balance
from utils.format import (
    format_trade_result,
    format_balance_text,
    format_error_message,
    format_help_text,
    format_debug_info
)
from utils.ping import check_jupiter_health
from utils.gpt import ask_chatgpt
from utils.menu import get_main_menu
from utils.pin import pin_welcome_message

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

        elif action == "menu":
            query.edit_message_text(
                text="📋 Main Menu:",
                reply_markup=get_main_menu(),
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
# === /buy Command ===
def buy(update: Update, context: CallbackContext):
    try:
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

# === /sell Command ===
def sell(update: Update, context: CallbackContext):
    try:
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
        update.message.reply_text(
            "📋 Main Menu:",
            reply_markup=get_main_menu(),
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        logger.error(f"/menu error: {e}")
        update.message.reply_text(
            format_error_message("⚠️ Menu load failed."),
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

# === Bot Launcher ===
def main():
    if not TELEGRAM_TOKEN:
        logger.error("❌ TELEGRAM_TOKEN missing. Cannot start bot.")
        return

    logger.info("🚀 Starting Flow X Bot...")
    updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher

    # Register slash commands for Telegram interface
    updater.bot.set_my_commands([
        ("start", "Launch bot"),
        ("buy", "Simulate Buy"),
        ("sell", "Simulate Sell"),
        ("balance", "Wallet Balance"),
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
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("buy", buy))
    dp.add_handler(CommandHandler("sell", sell))
    dp.add_handler(CommandHandler("balance", balance))
    dp.add_handler(CommandHandler("ping", ping))
    dp.add_handler(CommandHandler("help", help_cmd))
    dp.add_handler(CommandHandler("debug", debug))
    dp.add_handler(CommandHandler("menu", menu))
    dp.add_handler(CommandHandler("aiprompt", aiprompt))

    # Handle inline button callbacks
    dp.add_handler(CallbackQueryHandler(button))

    # Catch-all for non-command messages
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, fallback_message))

    # Start the bot
    updater.start_polling()
    logger.info("✅ Flow X Bot is live and listening...")
    updater.idle()


# === Fallback Text Response ===
def fallback_message(update: Update, context: CallbackContext):
    update.message.reply_text(
        "🤖 I didn’t understand that. Use /menu to get started.",
        parse_mode=ParseMode.HTML
    )


# === Entry Point ===
if __name__ == '__main__':
    main()
