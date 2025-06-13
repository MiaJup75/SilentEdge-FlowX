# === utils/debug.py ===
import sqlite3
from datetime import datetime, timedelta
import random
import os

DB_PATH = "trades.db"

def simulate_test_trades(n=10):
    if not os.path.exists(DB_PATH):
        print("Creating trades.db...")

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            side TEXT,
            amount REAL,
            price REAL,
            result TEXT,
            status TEXT,
            tx_hash TEXT,
            timestamp TEXT
        )
    ''')

    now = datetime.now()
    for i in range(n):
        side = random.choice(["BUY", "SELL"])
        amount = round(random.uniform(0.01, 0.05), 4)
        price = round(random.uniform(26000, 28000), 2)
        status = "executed"
        result = random.choice(["WIN", "LOSS"])
        tx_hash = f"TEST{i:03d}"
        timestamp = (now - timedelta(hours=i)).strftime("%Y-%m-%d %H:%M:%S")

        c.execute('''
            INSERT INTO trades (side, amount, price, status, tx_hash, result, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (side, amount, price, status, tx_hash, result, timestamp))

    conn.commit()
    conn.close()
    print(f"✅ {n} test trades inserted.")
