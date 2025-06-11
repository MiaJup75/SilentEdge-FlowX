from solana.rpc.api import Client
from solana.publickey import PublicKey

def get_wallet_balance(wallet_address: str) -> str:
    try:
        client = Client("https://api.mainnet-beta.solana.com")
        pubkey = PublicKey(wallet_address)
        result = client.get_balance(pubkey)

        if not result.get("result") or "value" not in result["result"]:
            return f"❌ Error: Invalid balance response → {result}"

        lamports = result["result"]["value"]
        sol = lamports / 1_000_000_000
        return f"{sol:.4f} SOL"

    except Exception as e:
        return f"❌ Exception in get_wallet_balance(): {str(e)}"
