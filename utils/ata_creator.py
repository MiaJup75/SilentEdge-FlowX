# utils/ata_creator.py
from solana.rpc.api import Client
from solana.publickey import PublicKey
from spl.token.instructions import create_associated_token_account
from solana.transaction import Transaction
from solana.system_program import SYS_PROGRAM_ID
from spl.token.constants import TOKEN_PROGRAM_ID, ASSOCIATED_TOKEN_PROGRAM_ID

client = Client("https://api.mainnet-beta.solana.com")

def create_token_account_if_needed(wallet_pubkey, payer_keypair, token_mint):
    from spl.token.instructions import get_associated_token_address
    ata = get_associated_token_address(PublicKey(wallet_pubkey), PublicKey(token_mint))

    res = client.get_account_info(ata)
    if res.get("result", {}).get("value"):
        return ata  # Already exists

    print(f"⚙️ Creating ATA for mint: {token_mint}")
    txn = Transaction()
    txn.add(
        create_associated_token_account(
            payer=PublicKey(wallet_pubkey),
            owner=PublicKey(wallet_pubkey),
            mint=PublicKey(token_mint)
        )
    )
    try:
        sig = client.send_transaction(txn, payer_keypair)
        print("✅ ATA created with tx:", sig["result"])
        return ata
    except Exception as e:
        print(f"❌ ATA creation failed: {e}")
        return None
