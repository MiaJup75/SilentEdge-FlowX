# signer.py

import base64
from solana.keypair import Keypair
import os

def load_wallet_from_env():
    secret_key_b64 = os.getenv("PHANTOM_SECRET_KEY")
    if not secret_key_b64:
        raise Exception("PHANTOM_SECRET_KEY is missing")

    secret_key_bytes = base64.b64decode(secret_key_b64)
    keypair = Keypair.from_secret_key(secret_key_bytes)
    return keypair
