import os
from bip_utils import Bip39SeedGenerator, Bip44, Bip44Coins, Bip44Changes
from solders.keypair import Keypair

def load_wallet():
    mnemonic_phrase = "zero another until inform oppose dentist clerk body apology certain ball midnight"
    
    # Generate seed from mnemonic
    seed_bytes = Bip39SeedGenerator(mnemonic_phrase).Generate()
    
    # Derive Solana key using BIP44 path m/44'/501'/0'/0'
    bip44_ctx = Bip44.FromSeed(seed_bytes, Bip44Coins.SOLANA).Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT).AddressIndex(0)
    priv_key_bytes = bip44_ctx.PrivateKey().Raw().ToBytes()

    # Build solders Keypair
    keypair = Keypair.from_seed(priv_key_bytes)

    print(f"🔐 Wallet Address: {keypair.pubkey()}")
    return keypair

def get_wallet_address(wallet):
    return str(wallet.pubkey())
