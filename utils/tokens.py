from solana.publickey import PublicKey
from solana.transaction import Transaction
from spl.token.instructions import transfer_checked, get_associated_token_address
from utils.signer import load_wallet_from_env
from solana.rpc.api import Client
import os

SOLANA_RPC_URL = os.getenv("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com")
client = Client(SOLANA_RPC_URL)

def transfer_spl_token(mint: str, recipient: str, amount: float, decimals: int = 6) -> str:
    sender_keypair = load_wallet_from_env()
    sender_pubkey = sender_keypair.public_key
    mint_pubkey = PublicKey(mint)
    recipient_pubkey = PublicKey(recipient)

    sender_ata = get_associated_token_address(sender_pubkey, mint_pubkey)
    recipient_ata = get_associated_token_address(recipient_pubkey, mint_pubkey)

    lamports = int(amount * (10 ** decimals))
    txn = Transaction()
    txn.add(
        transfer_checked(
            source=sender_ata,
            dest=recipient_ata,
            owner=sender_pubkey,
            mint=mint_pubkey,
            amount=lamports,
            decimals=decimals
        )
    )

    res = client.send_transaction(txn, sender_keypair)
    return res["result"]
