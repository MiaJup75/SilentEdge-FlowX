import os
import openai

# Load API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

# Ask ChatGPT a prompt and return the response
def ask_chatgpt(prompt):
    try:
        completion = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        return completion.choices[0].message["content"]
    except Exception as e:
        return f"⚠️ ChatGPT error: {str(e)}"
