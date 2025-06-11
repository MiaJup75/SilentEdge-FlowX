import os
from bip_utils import Bip39SeedGenerator, Bip44, Bip44Coins, Bip44Changes
from solders.keypair import Keypair

def load_wallet():
    mnemonic = os.getenv("PHANTOM_MNEMONIC")
    if not mnemonic:
        raise ValueError("Missing PHANTOM_MNEMONIC in environment variables")

    seed_bytes = Bip39SeedGenerator(mnemonic).Generate()

    # Derive Account 1 → External → Address Index 0
    account = Bip44.FromSeed(seed_bytes, Bip44Coins.SOLANA) \
                   .Purpose().Coin().Account(1) \
                   .Change(Bip44Changes.CHAIN_EXT) \
                   .AddressIndex(0)

    # ✅ Use UNCOMPRESSED public key (32 bytes)
    private_key = account.PrivateKey().Raw().ToBytes()
    public_key = account.PublicKey().RawUncompressed().ToBytes()  # ✅ FIXED

    keypair_bytes = private_key + public_key

    if len(keypair_bytes) != 64:
        raise ValueError(f"🔴 Combined key length is {len(keypair_bytes)} (expected 64)")

    return Keypair.from_bytes(keypair_bytes)

def get_wallet_address(wallet):
    return str(wallet.pubkey())
