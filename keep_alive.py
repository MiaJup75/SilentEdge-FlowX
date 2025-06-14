# keep_alive.py
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Flow X Bot is alive!", 200

def run():
    # Use a safe non-conflicting port like 8080
    app.run(host="0.0.0.0", port=8080)
