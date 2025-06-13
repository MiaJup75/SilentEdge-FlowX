# === utils/format.py ===
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

def format_usd(value: float) -> str:
    return f"${value:,.2f}"

def format_amount(value: float) -> str:
    return f"{value:,.4f}"

def format_trade_result(result):
    return f"""<b>🟢 Trade Executed</b>
Action: {result['side']}
Amount: {format_usd(result['amount'])}
Status: {result['status']}
TX: <code>{result['tx_hash']}</code>"""

def format_balance_text(balances):
    try:
        lines = ["<b>📊 Wallet Balance</b>"]
        for symbol, data in balances.items():
            amt = data.get("amount", 0)
            usd = data.get("usd", 0)
            emoji = "🟡" if amt == 0 else "🟢"
            lines.append(f"{emoji} {symbol}: {format_amount(amt)} ({format_usd(usd)})")
        return "\n".join(lines)
    except Exception as e:
        return f"<b>❌ Format Error</b>\n{str(e)}\n\nRaw Data:\n<code>{balances}</code>"

def format_error_message(msg):
    return f"❌ <b>Error</b>\n{msg}"

def format_help_text():
    return """<b>🆘 Commands:</b>
/start – Launch bot
/buy – Simulate Buy
/sell – Simulate Sell
/balance – Wallet Balance
/pnl – Daily PnL
/aiprompt – Ask ChatGPT
/debug – Bot Status
/ping – Jupiter Check
/menu – Button Menu
/pause – Pause/Resume
/limit – Set Daily Limit"""

def format_debug_info(wallet_address, live, trade_amt):
    return f"""<b>🔧 Debug Info</b>
Wallet: <code>{wallet_address}</code>
Live Mode: {'✅' if live else '❌'}
Trade Amount: {format_usd(trade_amt)}"""

def format_pnl_summary(day, trades, total_buy, total_sell, net_pnl, win_rate):
    emoji = "🔥" if net_pnl > 0 else "🧊" if net_pnl < 0 else "➖"
    return f"""📅 <b>Performance Summary – {day.title()}</b>

🔢 <b>Trades:</b> {trades}
📈 <b>Gross Sell:</b> {format_usd(total_sell)}
📉 <b>Gross Buy:</b> {format_usd(total_buy)}
🎯 <b>Win Rate:</b> {win_rate}%
{emoji} <b>Net PnL:</b> {format_usd(net_pnl)}
"""

def get_pnl_buttons(active="today"):
    options = [
        ("📆 Today", "today"),
        ("🕗 Yesterday", "yesterday"),
        ("📊 7d", "7d"),
        ("📅 30d", "30d"),
        ("📈 All Time", "alltime")
    ]
    buttons = [InlineKeyboardButton(
        f"{label} {'✅' if key == active else ''}",
        callback_data=f"pnl:{key}"
    ) for label, key in options]

    return InlineKeyboardMarkup([buttons])
