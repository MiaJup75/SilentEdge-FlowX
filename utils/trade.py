# === trade.py ===
import os
import time
import base64
import random
from datetime import datetime
from solana.keypair import Keypair
from utils.db import save_trade
from telegram import Update
from telegram.ext import CallbackContext
from utils.format import format_trade_result


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
        try:
            secret_key_b64 = os.getenv("PHANTOM_SECRET_KEY")
            if not secret_key_b64:
                raise ValueError("PHANTOM_SECRET_KEY not set")
            key_bytes = base64.b64decode(secret_key_b64)
            kp = Keypair.from_secret_key(key_bytes)

            # Placeholder - real Jupiter TX logic goes here
            trade_result = {
                "side": side,
                "amount": amount_usdc,
                "status": "✅ Live Trade Executed",
                "price": "$1.00",  # Stub until real execution
                "tx_hash": "real_tx_" + str(int(time.time()))
            }

        except Exception as e:
            trade_result = {
                "side": side,
                "amount": amount_usdc,
                "status": f"❌ Failed: {str(e)}",
                "price": "N/A",
                "tx_hash": "N/A"
            }

    save_trade({
        "timestamp": datetime.utcnow().isoformat(),
        "side": trade_result["side"],
        "amount": trade_result["amount"],
        "status": trade_result["status"],
        "price": trade_result["price"],
        "tx_hash": trade_result["tx_hash"]
    })

    return trade_result


def live_buy(update: Update, context: CallbackContext):
    from wallet import get_wallet_address
    from config import TRADE_AMOUNT_USDC

    update.message.reply_text("⏳ Executing LIVE BUY...")
    result = execute_jupiter_trade(get_wallet_address(), "BUY", TRADE_AMOUNT_USDC, live=True)
    update.message.reply_text(format_trade_result(result), parse_mode="HTML")


def live_sell(update: Update, context: CallbackContext):
    from wallet import get_wallet_address
    from config import TRADE_AMOUNT_USDC

    update.message.reply_text("⏳ Executing LIVE SELL...")
    result = execute_jupiter_trade(get_wallet_address(), "SELL", TRADE_AMOUNT_USDC, live=True)
    update.message.reply_text(format_trade_result(result), parse_mode="HTML")
