# utils/ata_checker.py

from solana.rpc.api import Client
from solana.publickey import PublicKey

RPC_URL = "https://api.mainnet-beta.solana.com"
client = Client(RPC_URL)

def has_token_account(wallet_address: str, token_mint: str) -> bool:
    try:
        resp = client.get_token_accounts_by_owner(
            PublicKey(wallet_address),
            opts={"mint": PublicKey(token_mint)}
        )
        return len(resp.get("result", {}).get("value", [])) > 0
    except Exception as e:
        print(f"[⚠ ATA Check Error] {e}")
        return False
