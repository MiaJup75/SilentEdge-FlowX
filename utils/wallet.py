import os
import base58
from solana.keypair import Keypair

# Load wallet from base58-encoded private key stored in env
def load_wallet():
    secret_key_b58 = os.getenv("SOLFLARE_PRIVATE_KEY")
    if not secret_key_b58:
        raise ValueError("Missing SOLFLARE_PRIVATE_KEY in environment variables.")
    
    secret_key_bytes = base58.b58decode(secret_key_b58)
    return Keypair.from_secret_key(secret_key_bytes)

def get_wallet_address(wallet):
    return str(wallet.public_key)
