import os
import requests
from solana.rpc.api import Client
from solana.publickey import PublicKey
from solana.rpc.types import TokenAccountOpts
from solana.transaction import Transaction
from solana.system_program import TransferParams, transfer
from spl.token.instructions import get_associated_token_address
from utils.signer import load_wallet_from_env
from utils.tokens import transfer_spl_token

# === Token Definitions (Canonical SPL Mints) ===
TOKEN_PAIRS = {
    "SOL": "So11111111111111111111111111111111111111112",
    "USDC": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
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

# === Get Wallet Address ===
def get_wallet_address(wallet=None):
    if wallet:
        return str(wallet.public_key)
    return os.getenv("SOLANA_WALLET_ADDRESS", str(load_wallet_from_env().public_key))

# === Price Fetcher ===
def fetch_price(mint_address: str) -> float:
    try:
        url = f"https://api.dexscreener.com/latest/dex/tokens/{mint_address}"
        res = requests.get(url, timeout=5).json()
        if "pairs" in res and res["pairs"]:
            return float(res["pairs"][0].get("priceUsd", 0.0))
    except Exception as e:
        print(f"❌ Error fetching price for {mint_address}: {e}")
    return 0.0

# === Wallet Balancer ===
def get_wallet_balance(wallet_address: str) -> tuple:
    balances = {}
    pubkey = PublicKey(wallet_address)

    for symbol, mint_address in TOKEN_PAIRS.items():
        try:
            if symbol == "SOL":
                result = client.get_balance(pubkey)
                amount = result.get("result", {}).get("value", 0) / 1_000_000_000
            else:
                token_accounts = client.get_token_accounts_by_owner(
                    pubkey,
                    TokenAccountOpts(mint=PublicKey(mint_address))
                )
                amount = 0.0
                if token_accounts.get("result", {}).get("value"):
                    ata_address = token_accounts["result"]["value"][0]["pubkey"]
                    token_info = client.get_token_account_balance(PublicKey(ata_address))
                    amount = float(token_info["result"]["value"].get("uiAmount", 0))

            price = fetch_price(mint_address)
            balances[symbol] = {
                "amount": round(amount, 4),
                "usd": round(amount * price, 2)
            }

        except Exception as e:
            print(f"⚠️ Error fetching {symbol}: {e}")
            balances[symbol] = {"amount": 0.0, "usd": 0.0}

    total_usd = sum(x["usd"] for x in balances.values())
    display = [f"💰 <b>Total Wallet Value:</b> ${total_usd:,.2f}\n"]

    for symbol, data in balances.items():
        percent = (data["usd"] / total_usd * 100) if total_usd else 0
        emoji = TOKEN_EMOJIS.get(symbol, "🔸")
        display.append(
            f"{emoji} <b>{symbol}</b>: {data['amount']:.4f} ≈ ${data['usd']:.2f} ({percent:.1f}%)"
        )

    return balances, "\n".join(display)

# === Transfer All ===
def transfer_all_tokens_and_sol(destination: str, balance_data: dict) -> list:
    tx_ids = []
    kp = load_wallet_from_env()
    dest = PublicKey(destination)

    # Transfer SOL
    sol_lamports = balance_data.get("SOL", {}).get("amount", 0) * 1e9
    if sol_lamports > 5000:
        tx = Transaction().add(
            transfer(
                TransferParams(
                    from_pubkey=kp.public_key,
                    to_pubkey=dest,
                    lamports=int(sol_lamports - 5000)
                )
            )
        )
        result = client.send_transaction(tx, kp)
        tx_ids.append(result.get("result"))

    # Transfer SPL Tokens
    for token in ["USDC", "wSOL"]:
        amt = balance_data.get(token, {}).get("amount", 0)
        if amt > 0:
            sig = transfer_spl_token(kp, destination, token, amt)
            tx_ids.append(sig)

    return tx_ids
