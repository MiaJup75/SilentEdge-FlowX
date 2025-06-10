# Flow X – SilentEdge Crypto Scalping Bot

**Flow X** is a fully automated, Telegram-connected crypto scalping and swing trading bot. Built for precision and speed, it executes live trades on Solana DEXes via Jupiter using your Solflare wallet.

---

## ⚙️ Features

- RSI-based scalping logic (more strategies coming)
- Auto-buy/sell with cooldowns and risk settings
- Solana-native trading via Jupiter Aggregator
- Telegram terminal with full command access
- Secure private key execution (never exposed)
- No Binance/KYC required

---

## 🚀 Deployment

Flow X runs on [Render.com](https://render.com) as a **Python Web Service**.

### 1. Environment Variables

Set these in Render:

- `TELEGRAM_TOKEN` — Your Telegram bot token
- `TELEGRAM_USER_ID` — Your Telegram user ID (for access control)
- `SOLFLARE_PRIVATE_KEY` — Your 12-word seed phrase (Solflare burner wallet)

### 2. Project Files

Make sure you have the following in your project:

- `main.py`
- `config.py`
- `requirements.txt`
- `render.yaml`
- `utils/` directory (logic modules)

---

## 📦 Roadmap

- [x] BTC Live Trading
- [ ] ETH / XRP support
- [ ] Advanced TA strategies
- [ ] Profit analytics
- [ ] Mirror wallet sniping
- [ ] UI dashboard for trade logs

---

**Not for public use. For SilentEdge internal testing only.**
