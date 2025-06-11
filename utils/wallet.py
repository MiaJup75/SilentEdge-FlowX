import os
from solders.keypair import Keypair
from solders.mnemonic import Mnemonic

def load_wallet():
    # Your 12-word mnemonic
    mnemonic_phrase = "zero another until inform oppose dentist clerk body apology certain ball midnight"
    
    # Load keypair from mnemonic (Solana standard derivation)
    keypair = Keypair.from_mnemonic(mnemonic_phrase)
    
    print(f"🔐 Wallet Address: {keypair.pubkey()}")
    return keypair

def get_wallet_address(wallet):
    return str(wallet.pubkey())
