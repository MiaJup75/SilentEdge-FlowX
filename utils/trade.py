import time
import random
from datetime import datetime
from utils.db import save_trade

def execute_jupiter_trade(wallet, side, amount_usdc, live=False):
    """
    Simulate or execute a trade via Jupiter aggregator.

    Args:
        wallet (str): Wallet address
        side (str): "BUY" or "SELL"
        amount_usdc (float): Trade amount in USDC
        live (bool): Whether to execute live or simulate

    Returns:
        dict: Formatted trade result
    """

    trade_result = {}

    # === Simulated Trade ===
    if not live:
        mock_price = round(random.uniform(0.9, 1.1), 4)
        trade_result = {
            "side": side,
            "amount": amount_usdc,
            "status": "✅ Simulated Trade",
            "price": f"${mock_price}",
            "tx_hash": "sim_tx_" + str(int(time.time()))
        }
    else:
        # === Live Trade Placeholder ===
        try:
            # TO DO: Replace with actual Jupiter API integration + wallet signing
            trade_result = {
                "side": side,
                "amount": amount_usdc,
                "status": "⚠️ Live Trade (Mocked)",
                "price": "TBD",
                "tx_hash": "live_tx_mock_" + str(int(time.time()))
            }
        except Exception as e:
            trade_result = {
                "side": side,
                "amount": amount_usdc,
                "status": f"❌ Failed: {str(e)}",
                "price": "N/A",
                "tx_hash": "N/A"
            }

    # === Log the trade ===
    save_trade({
        "timestamp": datetime.utcnow().isoformat(),
        "side": trade_result["side"],
        "amount": trade_result["amount"],
        "status": trade_result["status"],
        "price": trade_result["price"],
        "tx_hash": trade_result["tx_hash"]
    })

    return trade_result
