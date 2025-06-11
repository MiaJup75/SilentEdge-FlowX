import os
from bip_utils import Bip39SeedGenerator, Bip44, Bip44Coins, Bip44Changes
from solders.keypair import Keypair

def load_wallet():
    mnemonic = os.getenv("PHANTOM_MNEMONIC")
    if not mnemonic:
        raise ValueError("Missing PHANTOM_MNEMONIC in environment variables")

    seed_bytes = Bip39SeedGenerator(mnemonic).Generate()
    
    # 🔥 Derive Account #1 instead of Account #0
    account = Bip44.FromSeed(seed_bytes, Bip44Coins.SOLANA) \
                   .Purpose().Coin().Account(1) \
                   .Change(Bip44Changes.CHAIN_EXT).AddressIndex(0)

    private_key_bytes = account.PrivateKey().Raw().ToBytes()
    return Keypair.from_bytes(private_key_bytes)

def get_wallet_address(wallet):
    return str(wallet.pubkey())
