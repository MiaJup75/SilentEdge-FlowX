from solana.rpc.api import Client
from solana.publickey import PublicKey
from spl.token.instructions import get_associated_token_address
import base58

# Predefined list of popular SPL token mints
TOKEN_MINTS = {
    "USDC": "Es9vMFrzaCERsbyzNKzD4DM6YkT6rzdEDHHZLCXh4MfP",   # USDC Mainnet
    "wBTC": "9n4nbM75f5Ui33ZbPYXn59EwSgE8CGsHtAeTH5YFeJ9E",  # Wrapped BTC
}

def get_wallet_balance(wallet_address: str) -> dict:
    client = Client("https://api.mainnet-beta.solana.com")
    pubkey = PublicKey(wallet_address)
    balances = {}

    # Get native SOL balance
    try:
        result = client.get_balance(pubkey)
        lamports = result.get("result", {}).get("value", 0)
        balances["SOL"] = lamports / 1_000_000_000
    except Exception as e:
        print(f"Error fetching SOL balance: {e}")
        balances["SOL"] = 0.0

    # Get SPL token balances (e.g., USDC, wBTC)
    for symbol, mint in TOKEN_MINTS.items():
        try:
            ata = get_associated_token_address(pubkey, PublicKey(mint))
            token_info = client.get_token_account_balance(ata)
            amount = float(token_info.get("result", {}).get("value", {}).get("uiAmount", 0))
            balances[symbol] = amount
        except Exception as e:
            print(f"Error fetching {symbol} balance: {e}")
            balances[symbol] = 0.0

    return balances
