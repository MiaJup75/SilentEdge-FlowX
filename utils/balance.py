from solana.rpc.api import Client
from solana.publickey import PublicKey

def get_wallet_balance(wallet_address: str) -> dict:
    try:
        client = Client("https://api.mainnet-beta.solana.com")
        pubkey = PublicKey(wallet_address)
        result = client.get_balance(pubkey)

        if not result.get("result") or "value" not in result["result"]:
            print(f"❌ Error: Invalid balance response → {result}")
            return {"sol": 0.0}

        lamports = result["result"]["value"]
        sol = lamports / 1_000_000_000

        return {"sol": sol}  # ✅ Dict format expected by /balance

    except Exception as e:
        print(f"❌ Exception in get_wallet_balance(): {str(e)}")
        return {"sol": 0.0}
