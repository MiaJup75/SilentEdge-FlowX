import os
from bip_utils import Bip39SeedGenerator, Bip44, Bip44Coins, Bip44Changes
from solders.keypair import Keypair

def load_wallet():
    mnemonic = os.getenv("PHANTOM_MNEMONIC")
    if not mnemonic:
        raise ValueError("Missing PHANTOM_MNEMONIC in environment variables")

    seed_bytes = Bip39SeedGenerator(mnemonic).Generate()

    # ✅ Derive Account 1, not Account 0
    account = Bip44.FromSeed(seed_bytes, Bip44Coins.SOLANA) \
                   .Purpose().Coin().Account(1) \
                   .Change(Bip44Changes.CHAIN_EXT) \
                   .AddressIndex(0)

    private_key = account.PrivateKey().Raw().ToBytes()
    public_key = account.PublicKey().RawCompressed().ToBytes()

    return Keypair.from_bytes(private_key + public_key)

def get_wallet_address(wallet):
    return str(wallet.pubkey())
