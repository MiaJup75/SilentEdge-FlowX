# Flow X – SilentEdge Binance Scalping Bot

**Flow X** is a fully automated, Telegram-controlled scalping and swing trading bot built for Binance Spot. Designed for precision, stability, and consistent daily returns, it executes trades using RSI and volume-based strategies.

---

## ⚙️ Features

- ✅ **Binance Spot Integration** (USDC pairs only)
- ✅ **RSI-based scalping** with smart cooldowns
- ✅ **Auto-buy/sell** execution with take profit & stop loss logic
- ✅ **PnL tracking** and daily trade summaries
- ✅ **Telegram Bot Interface** for live control
- ✅ **Daily limits**, emergency pause, and debug commands
- ✅ **No Solana or DEX dependencies**

---

## 🚀 Deployment (via Render)

Flow X runs as a **Python Web Service** hosted on [Render.com](https://render.com).

### 1. Required Environment Variables

Set these inside your Render service:

| Key                  | Description                         |
|----------------------|-------------------------------------|
| `TELEGRAM_TOKEN`     | Telegram Bot API token              |
| `TELEGRAM_USER_ID`   | Your personal Telegram user ID      |
| `BINANCE_API_KEY`    | Your Binance Spot API key           |
| `BINANCE_SECRET_KEY` | Your Binance Spot API secret        |
| `WEBHOOK_URL`        | Your Render service's public URL    |
| `PORT`               | Set to `10000`                      |

---

### 2. Project Structure

Ensure your project includes the following:

📦 FlowX/
├── main.py
├── config.py
├── config.json
├── requirements.txt
├── render.yaml
├── keep_alive.py
├── state_manager.py
├── pause_limit.py
├── handlers/
│   └── pnl_handlers.py
├── utils/
│   ├── binance_trade.py
│   ├── balance.py
│   ├── db.py
│   ├── format.py
│   ├── format_balance.py
│   ├── reporting.py
│   ├── charts.py
│   ├── debug.py
│   ├── pin.py
│   └── pnl.py

---

## 📈 Roadmap

- [x] ✅ BTC/USDC live trading
- [x] ✅ PnL tracking with daily Telegram reports
- [ ] ETH/USDC + XRP/USDC support
- [ ] Trend momentum + EMA strategies
- [ ] Copy-trade mode (friend wallet sync)
- [ ] Optional Telegram inline control panel
- [ ] Visual stats dashboard (web UI)

---

**🔒 Internal Only:**  
This project is for SilentEdge private use and is not open source or licensed for redistribution.
