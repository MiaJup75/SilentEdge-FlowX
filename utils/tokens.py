import os
from solana.publickey import PublicKey
from solana.transaction import Transaction
from solana.rpc.api import Client
from spl.token.instructions import (
    get_associated_token_address,
    transfer_checked,
    TransferCheckedParams,
)
from spl.token.constants import TOKEN_PROGRAM_ID
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

    # Convert to lamports
    lamports = int(amount * (10 ** decimals))

    # Build transaction with correct params object
    txn = Transaction()
    txn.add(
        transfer_checked(
            TransferCheckedParams(
                program_id=TOKEN_PROGRAM_ID,
                source=sender_ata,
                mint=mint_pubkey,
                dest=recipient_ata,
                owner=sender_pubkey,
                amount=lamports,
                decimals=decimals,
                signers=[]
            )
        )
    )

    # Send it
    res = client.send_transaction(txn, sender_keypair)
    return res["result"]
