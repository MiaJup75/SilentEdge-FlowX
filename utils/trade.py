import time
import random

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

    # === Simulated Trade ===
    if not live:
        mock_price = round(random.uniform(0.9, 1.1), 4)
        return {
            "side": side,
            "amount": amount_usdc,
            "status": "✅ Simulated Trade",
            "price": f"${mock_price}",
            "tx_hash": "sim_tx_" + str(int(time.time()))
        }

    # === Live Trade Placeholder ===
    try:
        # TO DO: Replace with actual Jupiter API integration + wallet signing
        return {
            "side": side,
            "amount": amount_usdc,
            "status": "⚠️ Live Trade (Mocked)",
            "price": "TBD",
            "tx_hash": "live_tx_mock_" + str(int(time.time()))
        }
    except Exception as e:
        return {
            "side": side,
            "amount": amount_usdc,
            "status": f"❌ Failed: {str(e)}",
            "price": "N/A",
            "tx_hash": "N/A"
        }
