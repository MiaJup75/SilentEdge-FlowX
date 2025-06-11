def format_trade_result(result):
    return f"""<b>🟢 Trade Executed</b>
Action: {result['side']}
Amount: ${result['amount']}
Status: {result['status']}
TX: <code>{result['tx_hash']}</code>"""

def format_balance_text(balances):
    try:
        lines = ["<b>📊 Wallet Balance</b>"]
        for symbol, data in balances.items():
            amt = data.get("amount", 0)
            usd = data.get("usd", 0)
            emoji = "🟡" if amt == 0 else "🟢"
            lines.append(f"{emoji} {symbol}: {amt:.4f} (${usd:,.2f})")
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
/aiprompt – Ask ChatGPT
/debug – Bot Status
/ping – Jupiter Check
/menu – Button Menu"""

def format_debug_info(wallet_address, live, trade_amt):
    return f"""<b>🔧 Debug Info</b>
Wallet: <code>{wallet_address}</code>
Live Mode: {'✅' if live else '❌'}
Trade Amount: ${trade_amt}"""
