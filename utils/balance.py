from solana.rpc.api import Client

SOLANA_RPC = "https://api.mainnet-beta.solana.com"
client = Client(SOLANA_RPC)

def get_wallet_balance(wallet):
    pubkey = wallet.pubkey()
    sol_balance = client.get_balance(pubkey)["result"]["value"] / 1e9
    return {"sol": sol_balance}
