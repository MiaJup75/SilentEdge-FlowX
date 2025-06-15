import os
from utils.wallet import get_wallet_address
from utils.tokens import transfer_spl_token
from solana.rpc.api import Client
from solana.keypair import Keypair
from solana.transaction import Transaction
from solana.publickey import PublicKey
from solana.system_program import TransferParams, transfer
from utils.signer import load_wallet_from_env

SOLANA_RPC_URL = os.getenv("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com")
client = Client(SOLANA_RPC_URL)

DESTINATION = "8xfd61QP7PA2zkeazJvTCYCwLj9eMqodZ1uUW19SEoL6"  # 🔁 replace with actual Phantom address

# === SPL Tokens to Withdraw ===
TOKENS = {
    "USDC": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
    "wBTC": "9n4nbM75f5Ui33ZbPYXn59EwSgE8CGsHtAeTH5YFeJ9E",
    "wETH": "7vfCXTz6Xn9PafWz6ZrYT4hwTnTqQZKrj6kzzF7QjZqx",
    "wXRP": "6p9hY3F7v2KQhRJgkzGwXeMTufKYdcG89h6K9bGVznhu",
}

DECIMALS = {
    "USDC": 6,
    "wBTC": 6,
    "wETH": 6,
    "wXRP": 6,
}

def transfer_sol_if_possible(sender_keypair, dest_pubkey):
    balance = client.get_balance(sender_keypair.public_key)["result"]["value"]
    if balance < 10000:  # ~0.00001 SOL
        print("⚠️ Not enough SOL to send.")
        return
    lamports = balance - 5000  # Leave buffer
    txn = Transaction()
    txn.add(
        transfer(
            TransferParams(
                from_pubkey=sender_keypair.public_key,
                to_pubkey=dest_pubkey,
                lamports=lamports
            )
        )
    )
    client.send_transaction(txn, [sender_keypair])
    print(f"✅ Sent ~{lamports/1e9:.6f} SOL to {dest_pubkey}")

def main():
    sender_keypair = load_wallet_from_env()
    sender_address = str(sender_keypair.public_key)
    dest_pubkey = PublicKey(DESTINATION)

    print(f"📤 Withdrawing from {sender_address} to {DESTINATION}...")

    # Transfer SOL
    transfer_sol_if_possible(sender_keypair, dest_pubkey)

    # Transfer SPLs
    for symbol, mint in TOKENS.items():
        try:
            result = transfer_spl_token(mint, DESTINATION, 999999, decimals=DECIMALS[symbol])  # send max
            print(f"✅ {symbol} transfer result: {result}")
        except Exception as e:
            print(f"❌ {symbol} transfer failed: {e}")

if __name__ == "__main__":
    main()
