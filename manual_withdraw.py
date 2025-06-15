import os
from solana.publickey import PublicKey
from solana.rpc.api import Client
from solana.transaction import Transaction
from solana.system_program import TransferParams, transfer

from utils.signer import load_wallet_from_env
from utils.wallet import TOKEN_PAIRS
from utils.tokens import transfer_spl_token

# === Config ===
DEST_WALLET = "8xfd61QP7PA2zkeazJvTCYCwLj9eMqodZ1uUW19SEoL6"
SOLANA_RPC = os.getenv("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com")
client = Client(SOLANA_RPC)


def transfer_sol():
    try:
        kp = load_wallet_from_env()
        source_pub = kp.public_key
        dest_pub = PublicKey(DEST_WALLET)

        balance_response = client.get_balance(source_pub)
        sol_balance = balance_response["result"]["value"]

        if sol_balance < 10000:
            print("⚠️ Not enough SOL to send.")
            return

        lamports = sol_balance - 10000  # leave a tiny buffer
        tx = Transaction()
        tx.add(transfer(TransferParams(
            from_pubkey=source_pub,
            to_pubkey=dest_pub,
            lamports=lamports
        )))
        sig = client.send_transaction(tx, kp)["result"]
        print(f"✅ SOL sent: {lamports / 1e9:.6f} → {DEST_WALLET}")
        print(f"🔗 https://solscan.io/tx/{sig}")
    except Exception as e:
        print(f"❌ SOL transfer failed: {e}")


def transfer_spl_tokens():
    kp = load_wallet_from_env()
    for symbol, mint in TOKEN_PAIRS.items():
        if symbol == "SOL":
            continue
        try:
            sig = transfer_spl_token(kp, mint, DEST_WALLET)
            print(f"✅ {symbol} sent → {DEST_WALLET}")
            print(f"🔗 https://solscan.io/tx/{sig}")
        except Exception as e:
            print(f"❌ {symbol} transfer failed: {e}")


if __name__ == "__main__":
    transfer_sol()
    transfer_spl_tokens()
