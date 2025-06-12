# === utils/reporting.py ===
import os
import datetime
from telegram import ParseMode
from utils.pnl import calculate_daily_pnl  # Assumes this exists or mock logic inside

# === Daily PnL Summary Sender ===
def send_daily_pnl_summary(context):
    chat_id = os.getenv("OWNER_CHAT_ID")
    if not chat_id:
        return

    try:
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        pnl_data = calculate_daily_pnl()  # Replace with actual logic as needed

        # Format the report
        text = (
            f"📅 <b>Daily Trade Summary – {today}</b>\n\n"
            f"🔢 <b>Trades Executed:</b> {pnl_data['trades']}\n"
            f"📈 <b>Win Rate:</b> {pnl_data['win_rate']}%\n"
            f"💵 <b>Net PnL:</b> ${pnl_data['net_pnl']:.2f}\n"
        )

        context.bot.send_message(
            chat_id=int(chat_id),
            text=text,
            parse_mode=ParseMode.HTML
        )

    except Exception as e:
        print(f"❌ Failed to send PnL report: {e}")

# === Scheduler Hook (main.py) ===
# In main.py > after dispatcher setup:
from apscheduler.schedulers.background import BackgroundScheduler
from utils.reporting import send_daily_pnl_summary

scheduler = BackgroundScheduler()
scheduler.add_job(
    send_daily_pnl_summary,
    'cron',
    hour=9,
    minute=0,
    timezone='Asia/Bangkok',
    args=[updater.job_queue]
)
scheduler.start()
