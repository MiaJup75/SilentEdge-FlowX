import os
from solana.rpc.api import Client
from solana.transaction import Transaction
from solana.system_program import TransferParams, transfer
from solana.publickey import PublicKey
from spl.token.instructions import transfer_checked, get_associated_token_address, TOKEN_PROGRAM_ID
from utils.signer import load_wallet_from_env

# === Config ===
SOLANA_RPC_URL = os.getenv("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com")
DESTINATION = "8xfd61QP7PA2zkeazJvTCYCwLj9eMqodZ1uUW19SEoL6"  # your Phantom wallet
client = Client(SOLANA_RPC_URL)

# === Load wallet
kp = load_wallet_from_env()
source = kp.public_key
dest = PublicKey(DESTINATION)

# === Transfer SOL
try:
    balance = client.get_balance(source)["result"]["value"]
    lamports = balance - 5000
    if lamports > 0:
        tx = Transaction().add(
            transfer(TransferParams(
                from_pubkey=source,
                to_pubkey=dest,
                lamports=lamports
            ))
        )
        sig = client.send_transaction(tx, kp)["result"]
        print(f"✅ Sent SOL: https://solscan.io/tx/{sig}")
    else:
        print("⚠️ Not enough SOL to send.")
except Exception as e:
    print("❌ SOL transfer failed:", e)

# === Transfer USDC
try:
    MINT = PublicKey("EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v")  # USDC
    decimals = 6
    ata_src = get_associated_token_address(source, MINT)
    ata_dest = get_associated_token_address(dest, MINT)
    balance_data = client.get_token_account_balance(ata_src)
    amount = float(balance_data["result"]["value"]["uiAmount"])
    if amount > 0:
        tx = Transaction().add(
            transfer_checked(
                program_id=TOKEN_PROGRAM_ID,
                source=ata_src,
                mint=MINT,
                dest=ata_dest,
                owner=source,
                amount=int(amount * (10**decimals)),
                decimals=decimals
            )
        )
        sig = client.send_transaction(tx, kp)["result"]
        print(f"✅ Sent USDC: https://solscan.io/tx/{sig}")
    else:
        print("⚠️ No USDC to send.")
except Exception as e:
    print("❌ USDC transfer failed:", e)
