import os
import base64
from solders.keypair import Keypair

def load_wallet():
    # Expecting base64-encoded 64-byte secret key (not base58!)
    base64_key = os.getenv("SOLFLARE_PRIVATE_KEY")
    if not base64_key:
        raise ValueError("Missing SOLFLARE_PRIVATE_KEY in environment")

    secret_key_bytes = base64.b64decode(base64_key)

    # Debug statements to verify correct decoding
    print(f"🔍 Decoded secret key length: {len(secret_key_bytes)}")
    print(f"🔑 First 10 bytes: {list(secret_key_bytes[:10])}")

    if len(secret_key_bytes) != 64:
        raise ValueError("SOLFLARE_PRIVATE_KEY must decode to 64 bytes")

    return Keypair.from_bytes(secret_key_bytes)

def get_wallet_address(wallet):
    return str(wallet.pubkey())
