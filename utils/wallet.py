import base58
import os
from solders.keypair import Keypair
from solana.rpc.api import Client

def load_wallet():
    base58_key = os.getenv("SOLFLARE_PRIVATE_KEY")
    if not base58_key:
        raise ValueError("Missing SOLFLARE_PRIVATE_KEY env variable.")
    secret_key_bytes = base58.b58decode(base58_key)
    return Keypair.from_bytes(secret_key_bytes)

def get_wallet_address(wallet):
    return str(wallet.pubkey())
