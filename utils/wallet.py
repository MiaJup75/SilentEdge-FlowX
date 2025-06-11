import os
from bip_utils import Bip39SeedGenerator, Bip44, Bip44Coins, Bip44Changes
from solders.keypair import Keypair

def load_wallet():
    mnemonic = os.getenv("PHANTOM_MNEMONIC")
    if not mnemonic:
        raise ValueError("Missing PHANTOM_MNEMONIC in environment variables")

    seed_bytes = Bip39SeedGenerator(mnemonic).Generate()

    account = Bip44.FromSeed(seed_bytes, Bip44Coins.SOLANA) \
                   .Purpose().Coin().Account(1) \
                   .Change(Bip44Changes.CHAIN_EXT) \
                   .AddressIndex(0)

    private_key = account.PrivateKey().Raw().ToBytes()
    full_public_key = account.PublicKey().RawUncompressed().ToBytes()

    # ✅ Strip prefix byte to get 32-byte public key
    public_key = full_public_key[1:33]  # ⚠️ Skip first byte (0x04), keep next 32

    keypair_bytes = private_key + public_key

    if len(keypair_bytes) != 64:
        raise ValueError(f"🔴 Combined key length is {len(keypair_bytes)} (expected 64)")

    return Keypair.from_bytes(keypair_bytes)

def get_wallet_address(wallet):
    return str(wallet.pubkey())
