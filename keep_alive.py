# keep_alive.py

from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "✅ Flow X Bot is alive!", 200

def run():
    app.run(host="0.0.0.0", port=8080)
