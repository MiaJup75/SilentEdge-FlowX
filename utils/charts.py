# === utils/charts.py ===
import sqlite3
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import os
import uuid

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

def generate_pnl_bar_chart(days=7):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    dates = []
    pnls = []

    for i in range(days - 1, -1, -1):
        day = datetime.now() - timedelta(days=i)
        start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)

        c.execute('''
            SELECT side, amount, price FROM trades
            WHERE timestamp BETWEEN ? AND ?
        ''', (start.strftime("%Y-%m-%d %H:%M:%S"), end.strftime("%Y-%m-%d %H:%M:%S")))

        rows = c.fetchall()
        total_buy = sum(float(a) * float(p or 0) for s, a, p in rows if s.upper() == "BUY")
        total_sell = sum(float(a) * float(p or 0) for s, a, p in rows if s.upper() == "SELL")
        pnl = round(total_sell - total_buy, 2)

        dates.append(day.strftime("%d %b"))
        pnls.append(pnl)

    conn.close()

    fig, ax = plt.subplots(figsize=(8, 4))
    bars = ax.bar(dates, pnls, color=["green" if p >= 0 else "red" for p in pnls])
    ax.set_title("📊 7-Day PnL Overview")
    ax.set_ylabel("Net PnL ($)")
    ax.axhline(0, color='black', linewidth=0.8)
    plt.xticks(rotation=45)

    for bar, val in zip(bars, pnls):
        height = bar.get_height()
        ax.annotate(f"${val:.2f}", xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3 if height >= 0 else -15),
                    textcoords="offset points", ha='center', fontsize=8, color='black')

    plt.tight_layout()
    path = os.path.join(CHART_DIR, "pnl_bar.png")
    plt.savefig(path)
    plt.close()

    return path

# ✅ This is the missing function for inline charts:
def generate_pnl_chart(data, label="PnL"):
    try:
        filename = f"pnl_chart_{uuid.uuid4().hex}.png"
        filepath = os.path.join("/tmp", filename)

        plt.figure(figsize=(5, 2.5))
        plt.plot(data, marker="o", linestyle="-", linewidth=2)
        plt.title(f"{label.upper()} PnL Chart")
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(filepath)
        plt.close()
        return filepath

    except Exception as e:
        print(f"[Chart Error] {e}")
        return None
