import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, CommandHandler, CallbackQueryHandler
from solana.rpc.api import Client
from solana.transaction import Transaction
from solana.publickey import PublicKey
from solana.system_program import TransferParams, transfer
from spl.token.instructions import transfer_checked
from spl.token.constants import TOKEN_PROGRAM_ID
from utils.signer import load_wallet_from_env
from base58 import b58decode

# Solana setup
SOLANA_RPC = os.getenv("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com")
client = Client(SOLANA_RPC)
WITHDRAW_ALL_STATE = {}

# SPL Token Mints
USDC_MINT = PublicKey("EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v")
WSOL_MINT = PublicKey("So11111111111111111111111111111111111111112")


def withdraw_all(update: Update, context: CallbackContext):
    if not context.args:
        update.message.reply_text("❌ Usage: /withdrawall <destination_wallet_address>")
        return

    recipient = context.args[0]
    if not recipient or len(recipient) < 32:
        update.message.reply_text("❌ Invalid wallet address.")
        return

    WITHDRAW_ALL_STATE[update.effective_chat.id] = recipient
    keyboard = [
        [
            InlineKeyboardButton("✅ Confirm", callback_data="confirm_all_withdraw"),
            InlineKeyboardButton("❌ Cancel", callback_data="cancel_all_withdraw"),
        ]
    ]
    update.message.reply_text(
        f"""Are you sure you want to withdraw all SOL and SPL tokens to:
<code>{recipient}</code>?""",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


def confirm_all(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    user_id = query.message.chat_id
    action = query.data

    if action == "cancel_all_withdraw":
        query.edit_message_text("❌ Withdrawal cancelled.")
        return

    if action == "confirm_all_withdraw":
        recipient = WITHDRAW_ALL_STATE.get(user_id)
        if not recipient:
            query.edit_message_text("❌ No destination wallet found.")
            return

        try:
            kp = load_wallet_from_env()
            source_pub = kp.public_key
            recipient_pub = PublicKey(recipient)

            # --- 1. Send SOL ---
            sol_balance = client.get_balance(source_pub)["result"]["value"]
            sol_tx_sig = None
            if sol_balance > 5000:
                sol_lamports = sol_balance - 5000
                tx = Transaction()
                tx.add(transfer(TransferParams(from_pubkey=source_pub, to_pubkey=recipient_pub, lamports=sol_lamports)))
                sol_tx_sig = client.send_transaction(tx, kp)["result"]

            # --- 2. Send USDC + wSOL (SPL Tokens) ---
            spl_tx = Transaction()
            sent_any_spl = False

            for mint in [USDC_MINT, WSOL_MINT]:
                source_token_accounts = client.get_token_accounts_by_owner(source_pub, {"mint": str(mint)})["result"]["value"]
                if not source_token_accounts:
                    continue

                source_token = PublicKey(source_token_accounts[0]["pubkey"])
                token_amount = int(source_token_accounts[0]["account"]["data"]["parsed"]["info"]["tokenAmount"]["amount"])
                decimals = int(source_token_accounts[0]["account"]["data"]["parsed"]["info"]["tokenAmount"]["decimals"])

                if token_amount > 0:
                    recipient_token_accounts = client.get_token_accounts_by_owner(recipient_pub, {"mint": str(mint)})["result"]["value"]
                    if not recipient_token_accounts:
                        continue  # Skip if recipient doesn't have token account

                    recipient_token = PublicKey(recipient_token_accounts[0]["pubkey"])
                    spl_tx.add(
                        transfer_checked(
                            program_id=TOKEN_PROGRAM_ID,
                            source=source_token,
                            mint=mint,
                            dest=recipient_token,
                            owner=source_pub,
                            amount=token_amount,
                            decimals=decimals,
                        )
                    )
                    sent_any_spl = True

            spl_tx_sig = None
            if sent_any_spl:
                spl_tx_sig = client.send_transaction(spl_tx, kp)["result"]

            msg = "✅ Withdraw complete.\n"
            if sol_tx_sig:
                msg += f"💸 Sent SOL – <a href='https://solscan.io/tx/{sol_tx_sig}'>View</a>\n"
            if spl_tx_sig:
                msg += f"🔁 Sent SPL Tokens – <a href='https://solscan.io/tx/{spl_tx_sig}'>View</a>\n"

            query.edit_message_text(msg, parse_mode="HTML")

        except Exception as e:
            query.edit_message_text(f"❌ Error during withdrawal:\n<code>{e}</code>", parse_mode="HTML")


# === Handlers to add to your main.py ===
withdraw_all_handler = CommandHandler("withdrawall", withdraw_all)
confirm_all_handler = CallbackQueryHandler(confirm_all, pattern="^confirm_all_withdraw|cancel_all_withdraw$")
