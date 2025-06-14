import os
import requests
from solana.rpc.api import Client
from solana.publickey import PublicKey
from spl.token.instructions import get_associated_token_address

# === Token Definitions ===
TOKEN_MINTS = {
    "SOL": "So11111111111111111111111111111111111111112",
    "USDC": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # ✅ Native USDC
    "wBTC": "9n4nbM75f5Ui33ZbPYXn59EwSgE8CGsHtAeTH5YFeJ9E",
    "wETH": "7vfCXTz6Xn9PafWz6ZrYT4hwTnTqQZKrj6kzzF7QjZqx",
    "wXRP": "6p9hY3F7v2KQhRJgkzGwXeMTufKYdcG89h6K9bGVznhu"
}

TOKEN_EMOJIS = {
    "SOL": "🪙",
    "USDC": "💵",
    "wBTC": "₿",
    "wETH": "🧪",
    "wXRP": "💧"
}

SOLANA_RPC_URL = os.getenv("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com")
client = Client(SOLANA_RPC_URL)

def fetch_price(mint: str) -> float:
    try:
        url = f"https://api.dexscreener.com/latest/dex/tokens/{mint}"
        response = requests.get(url, timeout=5)
        data = response.json()
        price = float(data["pairs"][0]["priceUsd"])
        return price
    except Exception as e:
        print(f"❌ Error fetching price for {mint}: {e}")
        return 0.0

def get_wallet_balance(wallet_address: str) -> tuple:
    balances = {}
    pubkey = PublicKey(wallet_address)

    for symbol, mint in TOKEN_MINTS.items():
        try:
            if symbol == "SOL":
                result = client.get_balance(pubkey)
                amount = result.get("result", {}).get("value", 0) / 1_000_000_000
            else:
                ata = get_associated_token_address(pubkey, PublicKey(mint))
                token_info = client.get_token_account_balance(ata)
                amount = float(token_info.get("result", {}).get("value", {}).get("uiAmount", 0))
            price = fetch_price(mint)
            balances[symbol] = {
                "amount": round(amount, 4),
                "usd": round(amount * price, 2)
            }
        except Exception as e:
            print(f"⚠️ Error fetching {symbol}: {e}")
            balances[symbol] = {"amount": 0.0, "usd": 0.0}

    total_usd = sum(token["usd"] for token in balances.values())
    display_lines = [f"💰 <b>Total Wallet Value:</b> ${round(total_usd, 2):,.2f}\n"]

    for symbol, data in balances.items():
        percent = (data["usd"] / total_usd * 100) if total_usd else 0
        emoji = TOKEN_EMOJIS.get(symbol, "🔸")
        display_lines.append(
            f"{emoji} <b>{symbol}</b>: {data['amount']:.4f} ≈ ${data['usd']:.2f} ({percent:.1f}%)"
        )

    balance_message = "\n".join(display_lines)
    return balances, balance_message
