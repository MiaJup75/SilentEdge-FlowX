from solders.keypair import Keypair
from solana.rpc.api import Client

# Load wallet from 12-word mnemonic (hardcoded for now)
def load_wallet():
    mnemonic = [
        "zero", "another", "until", "inform", "oppose", "dentist",
        "clerk", "body", "apology", "certain", "ball", "midnight"
    ]
    return Keypair.from_mnemonic(mnemonic)

def get_wallet_address(wallet):
    return str(wallet.pubkey())
