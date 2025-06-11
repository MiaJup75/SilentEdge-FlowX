import os
import requests
from solana.rpc.api import Client
from solana.publickey import PublicKey
from spl.token.instructions import get_associated_token_address

# Supported SPL token mints
TOKEN_MINTS = {
    "USDC": "Es9vMFrzaCERsbyzNKzD4DM6YkT6rzdEDHHZLCXh4MfP",   # USDC
    "wBTC": "9n4nbM75f5Ui33ZbPYXn59EwSgE8CGsHtAeTH5YFeJ9E",   # Wrapped BTC
}

BIRDEYE_API_KEY = os.getenv("BIRDEYE_API_KEY")
SOLANA_RPC_URL = "https://api.mainnet-beta.solana.com"
BIRDEYE_PRICE_URL = "https://public-api.birdeye.so/public/price"

client = Client(SOLANA_RPC_URL)

def fetch_price(mint: str) -> float:
    try:
        headers = {"X-API-KEY": BIRDEYE_API_KEY}
        url = f"{BIRDEYE_PRICE_URL}?address={mint}"
        response = requests.get(url, headers=headers, timeout=5)
        data = response.json()
        return float(data["data"]["value"])
    except Exception as e:
        print(f"❌ Error fetching price for {mint}: {e}")
        return 0.0

def get_wallet_balance(wallet_address: str) -> dict:
    balances = {}
    pubkey = PublicKey(wallet_address)

    # === Native SOL ===
    try:
        result = client.get_balance(pubkey)
        lamports = result.get("result", {}).get("value", 0)
        sol = lamports / 1_000_000_000
        sol_price = fetch_price("So11111111111111111111111111111111111111112")
        balances["SOL"] = {
            "amount": sol,
            "usd": sol * sol_price
        }
    except Exception as e:
        print(f"❌ Error fetching SOL: {e}")
        balances["SOL"] = {"amount": 0.0, "usd": 0.0}

    # === SPL Tokens ===
    for symbol, mint in TOKEN_MINTS.items():
        try:
            ata = get_associated_token_address(pubkey, PublicKey(mint))
            token_info = client.get_token_account_balance(ata)
            amount = float(token_info.get("result", {}).get("value", {}).get("uiAmount", 0))
            price = fetch_price(mint)
            balances[symbol] = {
                "amount": amount,
                "usd": amount * price
            }
        except Exception as e:
            print(f"⚠️ Error fetching {symbol}: {e}")
            balances[symbol] = {"amount": 0.0, "usd": 0.0}

    return balances
