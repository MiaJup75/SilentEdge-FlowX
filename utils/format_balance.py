# === utils/format_balance.py ===

def format_balance_message(balances: dict) -> str:
    if not balances:
        return "⚠️ No tokens found in this wallet."

    sorted_tokens = sorted(balances.items(), key=lambda x: x[1]['usd'], reverse=True)

    message_lines = ["📊 <b>Wallet Balance Summary</b>\n"]

    for token, info in sorted_tokens:
        amount = round(info.get("amount", 0.0), 6)
        usd_value = round(info.get("usd", 0.0), 2)

        icon = {
            "SOL": "🟡",
            "USDC": "💵",
            "BTC": "₿",
            "ETH": "🧪",
            "XRP": "💧"
        }.get(token, "🔹")

        line = f"{icon} <b>{token}</b>: {amount} ≈ <b>${usd_value}</b>"
        message_lines.append(line)

    total_usd = round(sum(v["usd"] for v in balances.values()), 2)
    message_lines.append(f"\n💰 <b>Total Wallet Value:</b> <code>${total_usd}</code>")

    return "\n".join(message_lines)
