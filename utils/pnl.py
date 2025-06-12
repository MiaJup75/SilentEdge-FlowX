import sqlite3
from datetime import datetime, timedelta
import os

DB_PATH = "trades.db"  # Update this path if your database is elsewhere

def log_trade(side, amount, price, status, tx_hash):
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
            timestamp TEXT NOT NULL
        )
    ''')

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute('''
        INSERT INTO trades (side, amount, price, status, tx_hash, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (side, amount, price, status, tx_hash, timestamp))

    conn.commit()
    conn.close()

def calculate_daily_pnl(day="today"):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    now = datetime.now()
    if day == "today":
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif day == "yesterday":
        start = (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    else:
        start = datetime.min

    end = start + timedelta(days=1)

    c.execute('''
        SELECT side, amount, price FROM trades
        WHERE timestamp BETWEEN ? AND ?
    ''', (start.strftime("%Y-%m-%d %H:%M:%S"), end.strftime("%Y-%m-%d %H:%M:%S")))

    rows = c.fetchall()
    conn.close()

    total_buy = 0
    total_sell = 0
    for side, amount, price in rows:
        price = price or 0  # fallback
        if side.upper() == "BUY":
            total_buy += amount * price
        elif side.upper() == "SELL":
            total_sell += amount * price

    trades_count = len(rows)
    pnl = round(total_sell - total_buy, 2)
    emoji = "📈" if pnl >= 0 else "📉"

    return f"""
📊 <b>Daily PnL Report ({day.title()})</b>
Total Trades: <b>{trades_count}</b>
Gross Buy: ${total_buy:,.2f}
Gross Sell: ${total_sell:,.2f}
{emoji} <b>Net PnL:</b> ${pnl:,.2f}
""".strip()
