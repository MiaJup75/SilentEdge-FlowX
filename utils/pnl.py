import sqlite3
import os
from datetime import datetime, timedelta
from utils.charts import generate_pnl_chart

DB_PATH = os.getenv("TRADE_DB_PATH", "trades.db")
TRADE_HISTORY_MAX = int(os.getenv("TRADE_HISTORY_MAX", 30))

# === Optional External Logger Stub ===
def log_to_webhook(trade: dict):
    webhook = os.getenv("LOGGING_WEBHOOK_URL")
    if not webhook:
        return
    try:
        import requests
        requests.post(webhook, json=trade)
    except Exception as e:
        print(f"❌ Remote logging failed: {e}")

# === Enhanced Trade Logger with Symbol Support ===
def log_trade(side, amount, price, status, tx_hash, result=None, symbol=None):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute('''
                CREATE TABLE IF NOT EXISTS trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    side TEXT NOT NULL,
                    amount REAL NOT NULL,
                    price REAL,
                    status TEXT,
                    tx_hash TEXT,
                    result TEXT,
                    symbol TEXT,
                    timestamp TEXT NOT NULL
                )
            ''')
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            c.execute('''
                INSERT INTO trades (side, amount, price, status, tx_hash, result, symbol, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (side, amount, price, status, tx_hash, result, symbol, timestamp))

        # Optional remote logging
        log_to_webhook({
            "side": side,
            "amount": amount,
            "price": price,
            "status": status,
            "tx_hash": tx_hash,
            "result": result,
            "symbol": symbol,
            "timestamp": timestamp
        })

    except Exception as e:
        print(f"⚠️ Failed to log trade: {e}")

# === Dynamic Time Window PnL (All Coins or Per Token) ===
def calculate_daily_pnl(day="today", symbol=None):
    try:
        now = datetime.now()
        if day == "today":
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=1)
        elif day == "yesterday":
            start = (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=1)
        elif day.endswith("d") and day[:-1].isdigit():
            days = int(day[:-1])
            start = now - timedelta(days=days)
            end = now
        else:
            start = datetime.min
            end = now

        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            query = '''
                SELECT side, amount, price, result FROM trades
                WHERE timestamp BETWEEN ? AND ?
            '''
            params = [start.strftime("%Y-%m-%d %H:%M:%S"), end.strftime("%Y-%m-%d %H:%M:%S")]

            if symbol:
                query += " AND symbol = ?"
                params.append(symbol.upper())

            c.execute(query, params)
            rows = c.fetchall()

        total_buy = total_sell = win_count = total_trades = 0
        history = []

        for side, amount, price, result in rows:
            price = price or 0
            pnl = round(amount * price, 4)

            if side.upper() == "BUY":
                total_buy += pnl
                history.append(-pnl)
            elif side.upper() == "SELL":
                total_sell += pnl
                history.append(pnl)
                if result and result.upper() == "WIN":
                    win_count += 1

            total_trades += 1

        net_pnl = round(total_sell - total_buy, 2)
        win_rate = round((win_count / total_trades) * 100, 2) if total_trades else 0

        return {
            "trades": total_trades,
            "net_pnl": net_pnl,
            "win_rate": win_rate,
            "history": history[-TRADE_HISTORY_MAX:]
        }

    except Exception as e:
        print(f"⚠️ Error calculating PnL for window [{day}]: {e}")
        return {
            "trades": 0,
            "net_pnl": 0,
            "win_rate": 0,
            "history": []
        }

# === PnL Summary Formatter ===
def format_pnl_summary(pnl_data: dict) -> str:
    try:
        net = pnl_data.get("net_pnl", 0)
        win_rate = pnl_data.get("win_rate", 0)
        trades = pnl_data.get("trades", 0)
        recent = pnl_data.get("history", [])

        chart = generate_pnl_chart(recent)

        return (
            f"<b>📊 Performance Summary</b>\n\n"
            f"🔢 <b>Trades:</b> {trades}\n"
            f"📈 <b>Win Rate:</b> {win_rate:.1f}% {score_emoji(win_rate)}\n"
            f"💵 <b>Net PnL:</b> ${net:.2f}\n\n"
            f"{chart}"
        )
    except Exception as e:
        return f"<b>❌ PnL Format Error:</b> {e}"

# === Adaptive Time Window Picker ===
def calculate_auto_pnl(symbol=None):
    today = calculate_daily_pnl("today", symbol)
    if today["trades"] >= 3:
        return today

    last7d = calculate_daily_pnl("7d", symbol)
    if last7d["trades"] >= 3:
        return last7d

    return calculate_daily_pnl("30d", symbol)

# === Win Rate Emoji Grader ===
def score_emoji(win_rate):
    if win_rate >= 80:
        return "🔥"
    elif win_rate >= 60:
        return "✅"
    elif win_rate >= 40:
        return "⚠️"
    else:
        return "🧊"
