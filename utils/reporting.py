# === utils/reporting.py ===
import os
import datetime
from telegram import ParseMode, InputMediaPhoto
from utils.pnl import calculate_daily_pnl
from utils.format import format_usd, format_pnl_summary
from utils.charts import generate_pnl_chart

# === Daily Image + Summary Auto Drop (9AM BKK) ===
def send_daily_pnl_chart(context):
    chat_id = os.getenv("OWNER_CHAT_ID")
    if not chat_id:
        return

    try:
        report = calculate_daily_pnl("today")
        summary = format_pnl_summary(report)
        chart_path = generate_pnl_chart(report["history"], "today")

        if os.path.exists(chart_path):
            with open(chart_path, "rb") as chart:
                context.bot.send_photo(
                    chat_id=int(chat_id),
                    photo=chart,
                    caption=summary,
                    parse_mode=ParseMode.HTML
                )
        else:
            context.bot.send_message(
                chat_id=int(chat_id),
                text=summary,
                parse_mode=ParseMode.HTML
            )

    except Exception as e:
        print(f"❌ Failed to send PnL chart: {e}")


# === Optional Text-Only Fallback (Manual Use or Debug) ===
def send_daily_pnl_summary(context):
    chat_id = os.getenv("OWNER_CHAT_ID")
    if not chat_id:
        return

    try:
        today = datetime.datetime.now().strftime("%d %b %Y")
        pnl_data = calculate_daily_pnl()

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
        print(f"❌ Failed to send PnL summary: {e}")
