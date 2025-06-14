import requests
import json
import time
import sys
from base64 import b64decode
from solders.keypair import Keypair
from solana.rpc.api import Client
from solana.transaction import Transaction
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

# === Ensure stdout is flushed for Render ===
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
        res = requests.get(JUPITER_QUOTE_URL, params=params, headers=headers, timeout=10)
        res.raise_for_status()
        return res.json()
    except Exception as e:
        print(f"[❌ Jupiter Quote Error] {e}")
        return {}

def execute_swap(wallet_address, private_key, from_token, to_token, amount_usdc, slippage=0.5):
    try:
        print(f"🔁 Initiating swap: ${amount_usdc} {from_token} → {to_token}")
        quote = get_swap_quote(from_token, to_token, amount_usdc, slippage)

        if not quote.get("routes"):
            return {"success": False, "error": "No valid routes returned by Jupiter"}

        best_route = quote["routes"][0]
        swap_req = {
            "route": best_route,
            "userPublicKey": wallet_address,
            "wrapUnwrapSOL": True,  # ✅ Required for SOL ↔ SPL token routing
            "useSharedAccounts": False,
            "useUserAccounts": True,
            "computeUnitPriceMicroLamports": 10000,
            "useSimulator": False
        }

        res = requests.post(JUPITER_SWAP_URL, json=swap_req, timeout=10)
        res.raise_for_status()
        swap_data = res.json()

        if "swapTransaction" not in swap_data:
            return {"success": False, "error": "Jupiter response missing transaction"}

        raw_tx = b64decode(swap_data["swapTransaction"])
        tx = Transaction.deserialize(raw_tx)
        kp = Keypair.from_bytes(private_key)
        tx.sign([kp])
        sig = client.send_raw_transaction(tx.serialize(), opts={"skip_preflight": True})

        return {
            "success": True,
            "side": f"{from_token}->{to_token}",
            "amount": amount_usdc,
            "price_estimate": round(float(best_route.get("outAmount", 0)) / 10**6, 6),
            "used_route": best_route["marketInfos"][0].get("label", "N/A"),
            "tx_hash": sig["result"]
        }

    except Exception as e:
        print(f"[❌ Swap Execution Error] {e}")
        return {"success": False, "error": str(e)}
