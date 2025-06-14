# utils/jupiter_engine.py

import requests
import json
import time
import sys
import base64
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solana.transaction import Transaction
from solana.rpc.api import Client
from utils.signer import load_wallet_from_env

# === Jupiter API Endpoints ===
JUPITER_QUOTE_URL = "https://quote-api.jup.ag/v6/quote"
JUPITER_SWAP_URL = "https://quote-api.jup.ag/v6/swap"

# === Token Mints ===
SOL_MINT = "So11111111111111111111111111111111111111112"
USDC_MINT = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"

# === Solana RPC ===
SOLANA_RPC = "https://api.mainnet-beta.solana.com"
client = Client(SOLANA_RPC)

# === Flush stdout for Render logs ===
sys.stdout.reconfigure(line_buffering=True)


def get_swap_quote(from_token, to_token, amount_usdc, slippage=0.5):
    try:
        amount_lamports = int(amount_usdc * 10**6)
        params = {
            "inputMint": from_token,
            "outputMint": to_token,
            "amount": amount_lamports,
            "slippageBps": int(slippage * 100),
            "onlyDirectRoutes": False,
            "swapMode": "ExactIn"
        }
        headers = {
            "Origin": "https://jup.ag",
            "User-Agent": "Mozilla/5.0"
        }

        print(f"🛰 Jupiter API Request: {JUPITER_QUOTE_URL} with {params}")
        res = requests.get(JUPITER_QUOTE_URL, params=params, headers=headers, timeout=10)
        res.raise_for_status()
        return res.json()
    except Exception as e:
        print(f"[❌ Jupiter Quote Error] {e}")
        return {}


def execute_swap(wallet_address, private_key, from_token, to_token, amount_usdc, slippage=0.5):
    try:
        print(f"🔁 Executing Swap | {amount_usdc} {from_token} → {to_token}")
        quote = get_swap_quote(from_token, to_token, amount_usdc, slippage)

        if not quote or "routes" not in quote or not quote["routes"]:
            return {"success": False, "error": "No valid Jupiter routes"}

        route = quote["routes"][0]
        swap_req = {
            "route": route,
            "userPublicKey": wallet_address,
            "wrapUnwrapSOL": True,
            "useSharedAccounts": False,
            "useUserAccounts": True,
            "computeUnitPriceMicroLamports": 10000,
            "useSimulator": False
        }

        print("📤 Requesting Jupiter Swap TX...")
        res = requests.post(JUPITER_SWAP_URL, json=swap_req, timeout=10)
        res.raise_for_status()
        swap_tx = res.json()

        if "swapTransaction" not in swap_tx:
            return {"success": False, "error": "Missing swap transaction from Jupiter"}

        encoded_tx = swap_tx["swapTransaction"]
        tx_data = base64.b64decode(encoded_tx)
        tx = Transaction.deserialize(tx_data)

        # === Add blockhash + fee payer ===
        print("🔑 Signing transaction...")
        kp = Keypair.from_bytes(private_key)
        blockhash = client.get_latest_blockhash()["result"]["value"]["blockhash"]
        tx.recent_blockhash = blockhash
        tx.fee_payer = kp.pubkey()

        tx.sign([kp])
        tx_sig = client.send_raw_transaction(tx.serialize(), opts={"skip_preflight": True})

        return {
            "success": True,
            "side": f"{from_token}->{to_token}",
            "amount": amount_usdc,
            "price_estimate": round(float(route.get("outAmount", 0)) / 10**6, 6),
            "used_route": route["marketInfos"][0].get("label", "N/A"),
            "tx_hash": tx_sig["result"]
        }

    except Exception as e:
        print(f"[❌ Swap Execution Error] {e}")
        return {"success": False, "error": str(e)}
