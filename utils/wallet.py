import os
from bip_utils import Bip39SeedGenerator, Bip44, Bip44Coins, Bip44Changes
from solders.keypair import Keypair

def load_wallet():
    mnemonic = os.getenv("PHANTOM_MNEMONIC")
    if not mnemonic:
        raise ValueError("Missing PHANTOM_MNEMONIC in environment variables")

    # Generate seed from mnemonic
    seed_bytes = Bip39SeedGenerator(mnemonic).Generate()
    
    # Derive Solana-compatible wallet (m/44'/501'/0'/0')
    bip44_def_ctx = Bip44.FromSeed(seed_bytes, Bip44Coins.SOLANA)
    account = bip44_def_ctx.Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT).AddressIndex(0)

    private_key_bytes = account.PrivateKey().Raw().ToBytes()
    return Keypair.from_bytes(private_key_bytes + account.PublicKey().RawCompressed().ToBytes())

def get_wallet_address(wallet):
    return str(wallet.pubkey())
