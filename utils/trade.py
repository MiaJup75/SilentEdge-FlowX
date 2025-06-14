import time
from datetime import datetime

from utils.ata_checker import has_token_account  # ✅ Correct import
from utils.db import save_trade
from utils.signer import load_wallet_from_env
from utils.format import format_trade_result
from utils.jupiter_engine import execute_swap
from config import TRADE_AMOUNT, SLIPPAGE_TOLERANCE, BASE_TOKEN, QUOTE_TOKEN


def execute_jupiter_trade(side, amount_usdc=TRADE_AMOUNT, live=False, slippage=SLIPPAGE_TOLERANCE):
    trade_result = {}

    if not live:
        mock_price = round(1 / 25 + (0.01 * (0.5 - time.time() % 1)), 4)
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
            wallet_address = str(kp.public_key)
            print("🔐 Loaded wallet public key:", wallet_address)
            print("🔐 Wallet secret key length:", len(kp.secret_key))

            from_token = BASE_TOKEN if side == "BUY" else QUOTE_TOKEN
            to_token = QUOTE_TOKEN if side == "BUY" else BASE_TOKEN

            print("📦 Trade Params:")
            print("→ Side:", side)
            print("→ From:", from_token)
            print("→ To:", to_token)
            print("→ Amount:", amount_usdc)
            print("→ Slippage:", slippage)

            # ✅ ATA Check
            has_ata = has_token_account(wallet_address, from_token)
            if not has_ata:
                alert_msg = (
                    "⚠️ <b>Token account missing!</b>\n"
                    "Try sending a small amount of the token to this wallet to initialize it:\n"
                    f"<code>{wallet_address}</code>"
                )
                print(alert_msg)
                trade_result = {
                    "side": side,
                    "amount": amount_usdc,
                    "status": "⚠ Jupiter rejected trade: Token account not found.",
                    "price": "N/A",
                    "tx_hash": "N/A",
                    "alert": alert_msg,
                    "retry_suggested": True
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

            # ✅ Live swap execution
            result = execute_swap(
                wallet_address=wallet_address,
                private_key=kp.secret_key,
                from_token=from_token,
                to_token=to_token,
                amount_usdc=amount_usdc,
                slippage=slippage
            )

            print("📬 Swap Result:", result)

            if result["success"]:
                trade_result = {
                    "side": side,
                    "amount": amount_usdc,
                    "status": "✅ Live Trade Executed",
                    "price": f"${result.get('price_estimate', '?')}",
                    "tx_hash": result.get("tx_hash", "N/A")
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
            print("🔥 UNCAUGHT EXCEPTION IN TRADE:", str(e))
            trade_result = {
                "side": side,
                "amount": amount_usdc,
                "status": f"❌ Error: {str(e)}",
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
