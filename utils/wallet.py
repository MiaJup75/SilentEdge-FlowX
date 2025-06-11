import os
import base58
from solana.keypair import Keypair

def load_wallet():
    key_b58 = os.getenv("SOLFLARE_PRIVATE_KEY")
    if not key_b58:
        raise ValueError("Missing SOLFLARE_PRIVATE_KEY")

    secret_key_bytes = base58.b58decode(key_b58)
    return Keypair.from_secret_key(secret_key_bytes)

def get_wallet_address(wallet):
    return str(wallet.public_key)
