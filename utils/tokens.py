import os
from solana.publickey import PublicKey
from solana.transaction import Transaction
from solana.rpc.api import Client
from spl.token.constants import TOKEN_PROGRAM_ID
from spl.token.instructions import transfer_checked, get_associated_token_address
from utils.signer import load_wallet_from_env

# === Solana RPC Setup ===
SOLANA_RPC_URL = os.getenv("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com")
client = Client(SOLANA_RPC_URL)

# === Transfer SPL Token Function ===
def transfer_spl_token(mint: str, recipient: str, amount: float, decimals: int = 6) -> str:
    # Load wallet and keys
    sender_keypair = load_wallet_from_env()
    sender_pubkey = sender_keypair.public_key
    mint_pubkey = PublicKey(mint)
    recipient_pubkey = PublicKey(recipient)

    # Associated token accounts
    sender_ata = get_associated_token_address(sender_pubkey, mint_pubkey)
    recipient_ata = get_associated_token_address(recipient_pubkey, mint_pubkey)

    # Amount in smallest units
    lamports = int(amount * (10 ** decimals))

    # Create transfer transaction
    txn = Transaction()
    txn.add(
        transfer_checked(
            TOKEN_PROGRAM_ID,          # <- Required program ID
            sender_ata,                # source
            mint_pubkey,               # mint
            recipient_ata,             # destination
            sender_pubkey,             # owner
            lamports,                  # amount
            decimals                   # decimals
        )
    )

    # Send transaction
    res = client.send_transaction(txn, sender_keypair)
    return res["result"]
