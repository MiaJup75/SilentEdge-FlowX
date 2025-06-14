# signer.py

import base64
import os
from solana.keypair import Keypair
from solana.publickey import PublicKey

# 🔐 Load Keypair from the SOLANA_SECRET_KEY (for signing transactions)
def load_wallet_from_env():
    secret_key_b64 = os.getenv("SOLANA_SECRET_KEY")
    if not secret_key_b64:
        raise Exception("SOLANA_SECRET_KEY is missing")
    secret_key_bytes = base64.b64decode(secret_key_b64)
    keypair = Keypair.from_secret_key(secret_key_bytes)
    return keypair

# 🧠 Always use this to get the correct public address from env
def load_wallet_public_key():
    env_address = os.getenv("SOLANA_WALLET_ADDRESS")
    if env_address:
        return PublicKey(env_address)
    return load_wallet_from_env().public_key
