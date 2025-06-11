import os
import base64
from solana.keypair import Keypair

def load_wallet():
    base64_key = os.getenv("SOLFLARE_PRIVATE_KEY")
    if not base64_key:
        raise ValueError("Missing SOLFLARE_PRIVATE_KEY in environment")

    secret_key_bytes = base64.b64decode(base64_key)
    print(f"🔍 Decoded secret key length: {len(secret_key_bytes)}")
    print(f"🔑 First 10 bytes: {list(secret_key_bytes[:10])}")

    return Keypair.from_secret_key(secret_key_bytes)

def get_wallet_address(wallet):
    return str(wallet.public_key)
