# utils/ata_checker.py

from solana.rpc.api import Client
from solana.publickey import PublicKey
from solana.rpc.types import TokenAccountOpts  # ✅ REQUIRED fix

RPC_URL = "https://api.mainnet-beta.solana.com"
client = Client(RPC_URL)

def check_ata_exists(wallet_address: str, token_mint: str) -> bool:
    try:
        accounts = client.get_token_accounts_by_owner(
            PublicKey(wallet_address),
            TokenAccountOpts(mint=PublicKey(token_mint))  # ✅ CORRECT USAGE
        )
        return bool(accounts.get("result", {}).get("value"))
    except Exception as e:
        print(f"[⚠ ATA Check Error] {e}")
        return False
