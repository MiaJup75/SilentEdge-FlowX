# === utils/ask_chatgpt.py ===

import os
import openai
import time

# Load API key and defaults
openai.api_key = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("OPENAI_MODEL", "gpt-4")
TIMEOUT = int(os.getenv("OPENAI_TIMEOUT", 10))
MAX_RETRIES = 3
RETRY_DELAY = 2  # base delay in seconds

# Optional system prompt (for AI persona or trading rules)
SYSTEM_PROMPT = os.getenv("OPENAI_SYSTEM_PROMPT", "You are a crypto trading assistant. Answer clearly and concisely.")

def ask_chatgpt(prompt: str, temperature: float = 0.7) -> str:
    """
    Sends a prompt to OpenAI's ChatGPT and returns a formatted response.
    Retries automatically on failure.

    Args:
        prompt (str): The user's message
        temperature (float): Creativity level

    Returns:
        str: ChatGPT response (formatted for Telegram)
    """
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = openai.ChatCompletion.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                request_timeout=TIMEOUT
            )
            text = response.choices[0].message["content"].strip()
            return f"🧠 <b>ChatGPT:</b>\n{text}"

        except Exception as e:
            if attempt == MAX_RETRIES:
                return f"⚠️ <b>ChatGPT Error (retry {attempt}/{MAX_RETRIES})</b>\n<code>{str(e)}</code>"
            else:
                time.sleep(RETRY_DELAY * attempt)  # exponential backoff
