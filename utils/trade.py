# trade.py

import os
import time
import random
from datetime import datetime
from telegram import Update
from telegram.ext import CallbackContext
from utils.db import save_trade
from utils.signer import load_wallet_from_env
from utils.format import format_trade_result
from jupiter_engine import execute_swap


def execute_jupiter_trade(side, amount_usdc=50.0, live=False):
    trade_result = {}

    if not live:
        mock_price = round(random.uniform(0.98, 1.02), 4)
        trade_result = {
            "side": side,
            "amount": amount_usdc,
            "status": "✅ Simulated Trade",
            "price": f"${mock_price}",
            "tx_hash": "sim_tx_" + str(int(time.time()))
        }
    else:
        try:
            kp = load_wallet_from_env()
            from_token = "So11111111111111111111111111111111111111112"  # SOL (mock)
            to_token = "Es9vMFrzaCER6Y2z8uVJ4dj8vBWcy1YH3LWrjdTtuDrk"  # USDC

            result = execute_swap(
                wallet_address=str(kp.public_key),
                private_key=kp.secret_key,
                from_token=from_token,
                to_token=to_token,
                amount_usdc=amount_usdc
            )

            if result["success"]:
                trade_result = {
                    "side": side,
                    "amount": amount_usdc,
                    "status": "✅ Live Trade Executed",
                    "price": f"${result.get('price_estimate', '?')}",
                    "tx_hash": "real_tx_" + str(int(time.time()))
                }
            else:
                trade_result = {
                    "side": side,
                    "amount": amount_usdc,
                    "status": f"❌ Failed: {result.get('error', 'Unknown')}",
                    "price": "N/A",
                    "tx_hash": "N/A"
                }

        except Exception as e:
            trade_result = {
                "side": side,
                "amount": amount_usdc,
                "status": f"❌ Error: {str(e)}",
                "price": "N/A",
                "tx_hash": "N/A"
            }

    # Save to DB
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
    from config import TRADE_AMOUNT_USDC
    update.message.reply_text("⏳ Executing LIVE BUY...")
    result = execute_jupiter_trade("BUY", TRADE_AMOUNT_USDC, live=True)
    update.message.reply_text(format_trade_result(result), parse_mode="HTML")


def live_sell(update: Update, context: CallbackContext):
    from config import TRADE_AMOUNT_USDC
    update.message.reply_text("⏳ Executing LIVE SELL...")
    result = execute_jupiter_trade("SELL", TRADE_AMOUNT_USDC, live=True)
    update.message.reply_text(format_trade_result(result), parse_mode="HTML")
