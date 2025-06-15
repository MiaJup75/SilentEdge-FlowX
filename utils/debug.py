# utils/debug.py

import sqlite3
from datetime import datetime, timedelta
import random
import os
import base64
from solana.keypair import Keypair

DB_PATH = "trades.db"

def simulate_test_trades(n=10):
    """
    Populate the trades.db with simulated trade entries.
    Useful for testing charts, PnL summaries, and daily reports.
    """
    if not os.path.exists(DB_PATH):
        print("📄 Creating trades.db...")

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
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
    """)

    now = datetime.now()
    for i in range(n):
        side = random.choice(["BUY", "SELL"])
        amount = round(random.uniform(0.01, 0.05), 4)
        price = round(random.uniform(26000, 28000), 2)
        result = random.choice(["WIN", "LOSS"])
        tx_hash = f"SIM_TX_{i:03}"
        timestamp = (now - timedelta(minutes=i*15)).strftime("%Y-%m-%d %H:%M:%S")

        c.execute("""
            INSERT INTO trades (side, amount, price, result, status, tx_hash, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (side, amount, price, result, "executed", tx_hash, timestamp))

    conn.commit()
    conn.close()
    print(f"✅ {n} test trades inserted successfully.")

def debug_loaded_key():
    """
    Display information about the loaded Solana keypair.
    Deprecated for Binance, but useful for legacy inspection.
    """
    b64 = os.getenv("SOLANA_SECRET_KEY")
    if not b64:
        print("❌ SOLANA_SECRET_KEY not found.")
        return

    try:
        key_bytes = base64.b64decode(b64)
        kp = Keypair.from_secret_key(key_bytes)
        print("✅ Keypair loaded successfully.")
        print("→ Public Key:", kp.public_key)
        print("→ Secret Key Bytes:", len(kp.secret_key))
    except Exception as e:
        print("❌ Error decoding keypair:", e)
