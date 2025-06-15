import time
from datetime import datetime
from utils.db import get_open_trades, save_trade
from utils.binance_trade import execute_binance_trade, get_binance_price
from config import BASE_TOKEN, QUOTE_TOKEN, TAKE_PROFIT_PERCENT, STOP_LOSS_PERCENT

# Optional: Add Telegram alert sender
from utils.telegram_alerts import send_alert  # create this module if not exists

def monitor_trades(interval=5):
    print("🚀 TP/SL Watcher started...")
    symbol = f"{BASE_TOKEN}{QUOTE_TOKEN}"

    while True:
        open_trades = get_open_trades(symbol)

        for trade in open_trades:
            entry_price = float(trade.get("price", 0))
            trade_id = trade.get("tx_hash")
            side = trade.get("side")

            if side != "BUY":
                continue  # Only monitor BUY trades for now

            current_price = get_binance_price(symbol)
            tp_price = entry_price * (1 + TAKE_PROFIT_PERCENT / 100)
            sl_price = entry_price * (1 - STOP_LOSS_PERCENT / 100)

            if current_price >= tp_price:
                result = execute_binance_trade("SELL", amount_usdc=trade["amount"], live=True)
                result["trigger"] = "TP"
                result["original_tx"] = trade_id
                save_trade(result)
                send_alert(f"🟢 TP Hit: {symbol} sold at ${current_price:.4f} (TP: ${tp_price:.4f})")

            elif current_price <= sl_price:
                result = execute_binance_trade("SELL", amount_usdc=trade["amount"], live=True)
                result["trigger"] = "SL"
                result["original_tx"] = trade_id
                save_trade(result)
                send_alert(f"🔴 SL Triggered: {symbol} sold at ${current_price:.4f} (SL: ${sl_price:.4f})")

        time.sleep(interval)

if __name__ == '__main__':
    monitor_trades()
