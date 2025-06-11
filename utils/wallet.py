import os
import base64
from solana.keypair import Keypair  # ✅ Correct import

def load_wallet():
    base64_key = os.getenv("PHANTOM_PRIVATE_KEY")
    if not base64_key:
        raise ValueError("Missing PHANTOM_PRIVATE_KEY in environment")

    secret_key_bytes = base64.b64decode(base64_key)
    if len(secret_key_bytes) != 64:
        raise ValueError("PHANTOM_PRIVATE_KEY must decode to 64 bytes")

    return Keypair.from_secret_key(secret_key_bytes)  # ✅ Correct method

def get_wallet_address(wallet):
    return str(wallet.public_key)  # ✅ Correct property
