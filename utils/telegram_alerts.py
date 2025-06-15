import os
import requests

# Load Telegram token and user ID from environment
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_USER_ID = os.getenv("TELEGRAM_USER_ID")

def send_alert(message: str):
    """
    Sends a simple text message to your Telegram via bot.
    """
    if not TELEGRAM_TOKEN or not TELEGRAM_USER_ID:
        print("❌ TELEGRAM_TOKEN or TELEGRAM_USER_ID not set")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_USER_ID,
        "text": message,
        "parse_mode": "HTML"
    }

    try:
        response = requests.post(url, json=payload)
        if response.status_code != 200:
            print(f"❌ Telegram Error: {response.text}")
    except Exception as e:
        print(f"❌ Failed to send Telegram alert: {e}")
