# === utils/chatgpt.py ===
import os
import openai
import time

# === Environment Configuration ===
openai.api_key = os.getenv("OPENAI_API_KEY")
GPT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4")
GPT_TIMEOUT = int(os.getenv("OPENAI_TIMEOUT", "15"))
GPT_TEMP = float(os.getenv("GPT_TEMP", "0.7"))
GPT_SYSTEM_PROMPT = os.getenv("OPENAI_SYSTEM_PROMPT", "You are a top 0.0001% crypto trading assistant. Be concise.")
GPT_ENABLED = os.getenv("GPT_ENABLED", "true").lower() == "true"
GPT_RETRY_MAX = int(os.getenv("GPT_RETRY_MAX", "2"))
GPT_PERSONA_ID = os.getenv("GPT_PERSONA_ID", "default")

# === Ask ChatGPT Handler ===
def ask_chatgpt(prompt):
    if not GPT_ENABLED:
        return "⚠️ GPT is currently disabled by admin."

    retries = 0
    while retries <= GPT_RETRY_MAX:
        try:
            response = openai.ChatCompletion.create(
                model=GPT_MODEL,
                timeout=GPT_TIMEOUT,
                temperature=GPT_TEMP,
                messages=[
                    {"role": "system", "content": GPT_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message["content"]
        except Exception as e:
            retries += 1
            if retries > GPT_RETRY_MAX:
                return f"❌ GPT error after {GPT_RETRY_MAX} retries: {str(e)}"
            time.sleep(1)
