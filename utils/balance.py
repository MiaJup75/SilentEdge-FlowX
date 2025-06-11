from solana.rpc.api import Client
from solana.publickey import PublicKey
from spl.token.instructions import get_associated_token_address
import requests

# Token mint addresses
TOKEN_MINTS = {
    "USDC": "Es9vMFrzaCERsbyzNKzD4DM6YkT6rzdEDHHZLCXh4MfP",   # USDC (SPL)
    "wBTC": "9n4nbM75f5Ui33ZbPYXn59EwSgE8CGsHtAeTH5YFeJ9E",  # Wrapped BTC
}

# Simple price fetch from Coingecko or Jupiter
def get_token_prices():
    try:
        response = requests.get(
            "https://price.jup.ag/v4/price?ids=SOL,USDC,wBTC",
            timeout=5
        )
        prices = response.json().get("data", {})
        return {
            "SOL": float(prices.get("SOL", {}).get("price", 0)),
            "USDC": float(prices.get("USDC", {}).get("price", 1)),
            "wBTC": float(prices.get("wBTC", {}).get("price", 0)),
        }
    except Exception as e:
        print(f"❌ Price fetch error: {e}")
        return {"SOL": 0, "USDC": 1, "wBTC": 0}

def get_wallet_balance(wallet_address: str) -> dict:
    client = Client("https://api.mainnet-beta.solana.com")
    pubkey = PublicKey(wallet_address)
    prices = get_token_prices()
    balances = {}

    # Native SOL
    try:
        sol_raw = client.get_balance(pubkey)
        lamports = sol_raw.get("result", {}).get("value", 0)
        sol = lamports / 1_000_000_000
        balances["sol"] = {
            "amount": sol,
            "usd": sol * prices["SOL"]
        }
    except Exception as e:
        print(f"❌ SOL error: {e}")
        balances["sol"] = {"amount": 0.0, "usd": 0.0}

    # SPL Tokens
    for symbol, mint in TOKEN_MINTS.items():
        try:
            ata = get_associated_token_address(pubkey, PublicKey(mint))
            token_info = client.get_token_account_balance(ata)
            amount = float(token_info.get("result", {}).get("value", {}).get("uiAmount", 0))
            balances[symbol.lower()] = {
                "amount": amount,
                "usd": amount * prices.get(symbol, 0)
            }
        except Exception as e:
            print(f"❌ {symbol} error: {e}")
            balances[symbol.lower()] = {"amount": 0.0, "usd": 0.0}

    return balances
