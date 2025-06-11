def format_trade_result(result):
    return f"""<b>🟢 Trade Executed</b>
Action: {result['side']}
Amount: ${result['amount']}
Status: {result['status']}
TX: <code>{result['tx_hash']}</code>"""

def format_balance_text(balance):
    return f"""<b>📊 Wallet Balance</b>
SOL: {balance['sol']:.4f}"""

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
