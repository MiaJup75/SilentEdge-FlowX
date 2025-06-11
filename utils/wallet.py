import os
from bip_utils import Bip39SeedGenerator, Bip44, Bip44Coins, Bip44Changes
from solders.keypair import Keypair

def load_wallet():
    mnemonic = os.getenv("PHANTOM_MNEMONIC")
    if not mnemonic:
        raise ValueError("Missing PHANTOM_MNEMONIC in environment variables")

    # Generate seed from mnemonic
    seed_bytes = Bip39SeedGenerator(mnemonic).Generate()

    # Derive Account 1, External Chain, Address 0
    account = Bip44.FromSeed(seed_bytes, Bip44Coins.SOLANA) \
                   .Purpose().Coin().Account(1) \
                   .Change(Bip44Changes.CHAIN_EXT) \
                   .AddressIndex(0)

    # ⚠️ Correct way: get full 64-byte secret key
    keypair_bytes = account.PrivateKey().Raw().ToExtended()

    # ✅ Use the correct format for solders.Keypair
    return Keypair.from_bytes(keypair_bytes)

def get_wallet_address(wallet):
    return str(wallet.pubkey())
