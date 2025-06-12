import os
import requests
from solana.rpc.api import Client
from solana.publickey import PublicKey
from spl.token.instructions import get_associated_token_address

# === Token Mints to Track ===
TOKEN_MINTS = {
    "SOL": "So11111111111111111111111111111111111111112",
    "USDC": "Es9vMFrzaCERsbyzNKzD4DM6YkT6rzdEDHHZLCXh4MfP",
    "wBTC": "9n4nbM75f5Ui33ZbPYXn59EwSgE8CGsHtAeTH5YFeJ9E",
    "wETH": "7vfCXTz6Xn9PafWz6ZrYT4hwTnTqQZKrj6kzzF7QjZqx",
    "wXRP": "6p9hY3F7v2KQhRJgkzGwXeMTufKYdcG89h6K9bGVznhu"
}

# === Emojis for UI ===
TOKEN_EMOJIS = {
    "SOL": "🪙",
    "USDC": "💵",
    "wBTC": "₿",
    "wETH": "🧪",
    "wXRP": "💧"
}

# === Config ===
BIRDEYE_API_KEY = os.getenv("BIRDEYE_API_KEY")
SOLANA_RPC_URL = "https://api.mainnet-beta.solana.com"
BIRDEYE_PRICE_URL = "https://public-api.birdeye.so/public/price"
client = Client(SOLANA_RPC_URL)


# === Price Fetcher ===
def fetch_price(mint: str) -> float:
    try:
        headers = {"X-API-KEY": BIRDEYE_API_KEY}
        url = f"{BIRDEYE_PRICE_URL}?address={mint}"
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        data = response.json()
        return float(data.get("data", {}).get("value", 0))
    except Exception as e:
        print(f"❌ Error fetching price for {mint}: {e}")
        return 0.0


# === Balance Fetcher ===
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
                "amount": amount,
                "usd": round(amount * price, 2)
            }
        except Exception as e:
            print(f"⚠️ Error fetching {symbol}: {e}")
            balances[symbol] = {"amount": 0.0, "usd": 0.0}

    # === Format Output ===
    total_usd = sum(t["usd"] for t in balances.values())
    display_lines = [f"💰 <b>Total Wallet Value:</b> ${round(total_usd, 2):,.2f}\n"]

    for symbol, data in balances.items():
        percent = (data["usd"] / total_usd * 100) if total_usd else 0
        emoji = TOKEN_EMOJIS.get(symbol, "🔸")
        display_lines.append(
            f"{emoji} <b>{symbol}</b>: {data['amount']:.4f} ≈ ${data['usd']:.2f} ({percent:.1f}%)"
        )

    balance_message = "\n".join(display_lines)
    return balances, balance
