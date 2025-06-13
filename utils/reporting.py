# === utils/reporting.py ===
import os
import datetime
from telegram import ParseMode
from utils.pnl import calculate_daily_pnl
from utils.format import format_usd  # ✅ Make sure this exists

# === Daily PnL Summary Sender ===
def send_daily_pnl_summary(context):
    chat_id = os.getenv("OWNER_CHAT_ID")
    if not chat_id:
        return

    try:
        today = datetime.datetime.now().strftime("%d %b %Y")
        pnl_data = calculate_daily_pnl()  # Replace with real logic or mock safely

        # Format the report
        text = (
            f"<b>📊 Daily Trade Summary</b> ({today})\n"
            f"📈 <b>Trades Executed:</b> {pnl_data['trades']}\n"
            f"✅ <b>Win Rate:</b> {pnl_data['win_rate']}%\n"
            f"💰 <b>Net PnL:</b> {format_usd(pnl_data['net_pnl'])}"
        )

        context.bot.send_message(
            chat_id=int(chat_id),
            text=text,
            parse_mode=ParseMode.HTML
        )

    except Exception as e:
        print(f"❌ Failed to send PnL report: {e}")
