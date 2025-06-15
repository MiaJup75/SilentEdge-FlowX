import os
from solana.rpc.api import Client
from solana.transaction import Transaction
from solana.publickey import PublicKey
from solana.system_program import TransferParams, transfer
from utils.signer import load_wallet_from_env
from utils.tokens import transfer_spl_token

DEST_WALLET = "8xfd61QP7PA2zkeazJvTCYCwLj9eMqodZ1uUW19SEoL6"  # <-- set your Phantom here

SOLANA_RPC = os.getenv("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com")
client = Client(SOLANA_RPC)
kp = load_wallet_from_env()
source_pub = kp.public_key

# === Transfer SOL ===
try:
    sol_balance = client.get_balance(source_pub)["result"]["value"]
    if sol_balance < 5000:
        print("⚠️ Not enough SOL to send.")
    else:
        lamports = sol_balance - 5000  # leave fee buffer
        tx = Transaction()
        tx.add(transfer(TransferParams(from_pubkey=source_pub, to_pubkey=PublicKey(DEST_WALLET), lamports=lamports)))
        sig = client.send_transaction(tx, kp)["result"]
        print(f"✅ Sent {lamports / 1e9:.5f} SOL to {DEST_WALLET}")
        print(f"🔗 https://solscan.io/tx/{sig}")
except Exception as e:
    print(f"❌ SOL transfer failed: {e}")

# === Transfer SPL Tokens ===
SPL_MINTS = {
    "USDC": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
    "wBTC": "9n4nbM75f5Ui33ZbPYXn59EwSgE8CGsHtAeTH5YFeJ9E",
    "wETH": "7vfCXTz6Xn9PafWz6ZrYT4hwTnTqQZKrj6kzzF7QjZqx",
    "wXRP": "6p9hY3F7v2KQhRJgkzGwXeMTufKYdcG89h6K9bGVznhu"
}

for symbol, mint in SPL_MINTS.items():
    try:
        sig = transfer_spl_token(client, kp, mint, DEST_WALLET)
        if sig:
            print(f"✅ Sent {symbol} → https://solscan.io/tx/{sig}")
        else:
            print(f"⚠️ No {symbol} balance to send.")
    except Exception as e:
        print(f"❌ {symbol} transfer failed: {e}")
