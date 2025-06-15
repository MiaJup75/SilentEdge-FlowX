# === utils/reporting.py ===
import os
import datetime
from telegram import ParseMode
from utils.pnl import calculate_daily_pnl
from utils.format import format_usd, format_pnl_summary
from utils.charts import generate_pnl_chart

# === Get Single or Multiple Chat IDs (support expansion) ===
def get_owner_chat_ids():
    ids = os.getenv("OWNER_CHAT_ID") or ""
    return [int(i.strip()) for i in ids.split(",") if i.strip().isdigit()]

# === Daily Image + Summary Auto Drop (9AM BKK) ===
def send_daily_pnl_chart(context):
    chat_ids = get_owner_chat_ids()
    if not chat_ids:
        print("❌ No valid OWNER_CHAT_ID found.")
        return

    try:
        report = calculate_daily_pnl("today")
        summary = format_pnl_summary(report)
        chart_path = generate_pnl_chart(report["history"], title="Today")

        print(f"📤 Sending PnL chart | Trades: {report['trades']} | PnL: ${report['net_pnl']} | Win Rate: {report['win_rate']}%")

        for chat_id in chat_ids:
            if os.path.exists(chart_path):
                with open(chart_path, "rb") as chart:
                    context.bot.send_photo(
                        chat_id=chat_id,
                        photo=chart,
                        caption=summary,
                        parse_mode=ParseMode.HTML
                    )
            else:
                context.bot.send_message(
                    chat_id=chat_id,
                    text="📊 Daily chart unavailable. Here's the text summary:\n\n" + summary,
                    parse_mode=ParseMode.HTML
                )

    except Exception as e:
        print(f"❌ Failed to send PnL chart: {e}")

# === Optional Text-Only Summary ===
def send_daily_pnl_summary(context):
    chat_ids = get_owner_chat_ids()
    if not chat_ids:
        print("❌ No valid OWNER_CHAT_ID found.")
        return

    try:
        today = datetime.datetime.now().strftime("%d %b %Y")
        pnl_data = calculate_daily_pnl("today")

        text = (
            f"<b>📊 Daily Trade Summary</b> ({today})\n"
            f"📈 <b>Trades Executed:</b> {pnl_data['trades']}\n"
            f"✅ <b>Win Rate:</b> {pnl_data['win_rate']}%\n"
            f"💰 <b>Net PnL:</b> {format_usd(pnl_data['net_pnl'])}"
        )

        print(f"📤 Text-only PnL summary | Trades: {pnl_data['trades']} | Net: ${pnl_data['net_pnl']} | Win Rate: {pnl_data['win_rate']}%")

        for chat_id in chat_ids:
            context.bot.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode=ParseMode.HTML
            )

    except Exception as e:
        print(f"❌ Failed to send PnL summary: {e}")
