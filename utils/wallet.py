import os
import base64
from solders.keypair import Keypair  # ✅ CORRECT import

def load_wallet():
    base64_key = os.getenv("SOLFLARE_PRIVATE_KEY")
    if not base64_key:
        raise ValueError("Missing SOLFLARE_PRIVATE_KEY in environment")

    secret_key_bytes = base64.b64decode(base64_key)
    print(f"🔍 Decoded secret key length: {len(secret_key_bytes)}")
    print(f"🔑 First 10 bytes: {list(secret_key_bytes[:10])}")

    if len(secret_key_bytes) != 64:
        raise ValueError("SOLFLARE_PRIVATE_KEY must decode to 64 bytes")

    return Keypair.from_bytes(secret_key_bytes)  # ✅ CORRECT constructor

def get_wallet_address(wallet):
    return str(wallet.pubkey())  # ✅ CORRECT method for `solders.Keypair`
