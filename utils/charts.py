# === utils/charts.py ===
import sqlite3
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import os

DB_PATH = "trades.db"
CHART_DIR = "charts"
os.makedirs(CHART_DIR, exist_ok=True)

def get_trades():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT side, amount, price, timestamp FROM trades ORDER BY timestamp ASC")
    rows = c.fetchall()
    conn.close()
    return rows

def generate_pnl_line_chart():
    trades = get_trades()
    daily_pnl = {}

    for side, amount, price, timestamp in trades:
        date = timestamp.split(" ")[0]
        pnl = amount * (price or 0)
        daily_pnl.setdefault(date, 0)

        if side.upper() == "BUY":
            daily_pnl[date] -= pnl
        elif side.upper() == "SELL":
            daily_pnl[date] += pnl

    dates = [datetime.strptime(d, "%Y-%m-%d") for d in sorted(daily_pnl.keys())]
    values = [daily_pnl[d.strftime("%Y-%m-%d")] for d in dates]

    plt.figure(figsize=(8, 4))
    plt.plot(dates, values, marker='o', linestyle='-', color='green' if sum(values) >= 0 else 'red')
    plt.axhline(0, color='black', linewidth=0.8, linestyle='--')
    plt.title("📈 Daily Net PnL")
    plt.ylabel("Profit / Loss ($)")
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    plt.xticks(rotation=45)
    plt.tight_layout()

    path = os.path.join(CHART_DIR, "pnl_line.png")
    plt.savefig(path)
    plt.close()
    return path

def generate_trade_volume_chart():
    trades = get_trades()
    times = []
    values = []
    colors = []

    for side, amount, price, timestamp in trades:
        dt = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
        total = amount * (price or 0)
        times.append(dt)
        values.append(total)
        colors.append('green' if side.upper() == "BUY" else 'red')

    plt.figure(figsize=(10, 4))
    plt.bar(times, values, width=0.02, color=colors, alpha=0.7)
    plt.title("📊 Trade Volume Over Time")
    plt.ylabel("USD")
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    plt.xticks(rotation=45)
    plt.tight_layout()

    path = os.path.join(CHART_DIR, "volume_bar.png")
    plt.savefig(path)
    plt.close()
    return path
