import sqlite3
from datetime import datetime, timedelta
import os
from utils.charts import generate_pnl_chart

DB_PATH = "trades.db"  # Update this path if your database is elsewhere

# === Enhanced Trade Logger with Win/Loss Calculation ===
def log_trade(side, amount, price, status, tx_hash, result=None):
    conn = sqlite3.connect(DB_PATH)
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
            timestamp TEXT NOT NULL
        )
    ''')

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute('''
        INSERT INTO trades (side, amount, price, status, tx_hash, result, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (side, amount, price, status, tx_hash, result, timestamp))

    conn.commit()
    conn.close()

# === Dynamic Time Window PnL ===
def calculate_daily_pnl(day="today"):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

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

    c.execute('''
        SELECT side, amount, price, result FROM trades
        WHERE timestamp BETWEEN ? AND ?
    ''', (start.strftime("%Y-%m-%d %H:%M:%S"), end.strftime("%Y-%m-%d %H:%M:%S")))

    rows = c.fetchall()
    conn.close()

    total_buy = 0
    total_sell = 0
    win_count = 0
    total_trades = 0
    history = []

    for side, amount, price, result in rows:
        price = price or 0
        pnl = amount * price

        if side.upper() == "BUY":
            total_buy += pnl
            history.append(-pnl)
        elif side.upper() == "SELL":
            total_sell += pnl
            history.append(pnl)
            if result == "WIN":
                win_count += 1
        total_trades += 1

    net_pnl = round(total_sell - total_buy, 2)
    win_rate = round((win_count / total_trades) * 100, 2) if total_trades else 0

    return {
        "trades": total_trades,
        "net_pnl": net_pnl,
        "win_rate": win_rate,
        "history": history[-30:]
    }

# === PnL Formatter ===
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
            f"📈 <b>Win Rate:</b> {win_rate}%\n"
            f"💵 <b>Net PnL:</b> ${net:.2f}\n\n"
            f"{chart}"
        )
    except Exception as e:
        return f"<b>❌ PnL Format Error:</b> {e}"
