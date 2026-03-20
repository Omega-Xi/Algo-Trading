# 🚀 Upstox Algo Trading Bot

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Upstox](https://img.shields.io/badge/Upstox-API%20V3-orange.svg)](https://upstox.com/developer/api/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

**Automated algorithmic trading system for NSE index options**  
*Real-time WebSocket streaming · Multi-timeframe analysis · Advanced risk management*

</div>

---

## 📋 Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Strategies](#strategies)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Risk Management](#risk-management)
- [Performance Reporting](#performance-reporting)
- [Contributing](#contributing)
- [License](#license)
- [Disclaimer](#disclaimer)

---

## 🔍 Overview

This is a production-ready algorithmic trading bot built on the **Upstox API V3**. It automates options trading on NSE indices using sophisticated technical analysis and real-time market data streaming.

### Key Highlights
- ✅ **Real-time WebSocket** connection for tick-by-tick data
- ✅ **Multi-timeframe analysis** (1, 3, 5, 10, 15 minutes)
- ✅ **Dynamic position sizing** based on available margin
- ✅ **ATR-based trailing stop-loss** with auto-update
- ✅ **Dry run mode** for safe backtesting
- ✅ **Comprehensive logging** and alert system
- ✅ **Trade journaling** with CSV export

---

## ✨ Features

### 📊 Data Processing
- Real-time tick aggregation into OHLC candles
- Multi-timeframe indicator calculations (ATR, MACD, EMA, RSI, ADX, VWAP, Bollinger Bands)
- Historical data preloading for accurate analysis

### 🎯 Trading Strategies

| Strategy | Description | Status |
|----------|-------------|--------|
| **MACD EMA** | MACD crossover with EMA smoothing | 🟢 **Active** |
| MACD RSI | MACD crossover + RSI confirmation | 🟡 Available |
| MACD ADX | Trend strength filter with ADX | 🟡 Available |
| VWAP RSI | VWAP breakout with RSI | 🟡 Available |
| Bollinger RSI | Mean reversion strategy | 🟡 Available |
| Golden Strategy | Hybrid trend + mean reversion | 🟡 Available |

### 🛡️ Risk Management
- **Position Sizing**: `Qty = (Margin × Risk%) / (Entry - Stop Loss)`
- **Trailing Stop**: `max(Current SL, Highest Price - ATR × 1.5)`
- **Risk per Trade**: Configurable (default 2%)
- **Risk-Reward Ratio**: Configurable (default 2:1)
- **Cooldown Period**: 30 seconds between trades

### 📈 Performance Tracking
- Automatic trade recording with entry/exit timestamps
- CSV export of all trades
- Performance metrics: win rate, profit factor, Sharpe ratio

---

## 🏗 Architecture

### System Flow

```mermaid
graph TD;
    Market[Market Data] --> WS[WebSocket Streamer];
    WS --> Buffer[Tick Buffer];
    Buffer --> Candles[Candle Factory];
    Candles --> Indicators[Indicator Engine];
    Indicators --> Strategy{Strategy Router};
    
    Strategy -->|Entry Signal| Sizing[Position Sizing];
    Strategy -->|Exit Signal| Exit[Exit Manager];
    
    Sizing --> Order[Order Execution];
    Order --> API[Upstox API];
    
    Exit --> Recorder[Trade Recorder];
    Recorder --> CSV[CSV Export];
    
    Alerts[Alerts] --> Notify[Notifications];
```

### Bot Lifecycle

```mermaid
graph LR;
    A[Authentication] --> B[Data Preload];
    B --> C[Market Sync];
    C --> D[WebSocket Connect];
    D --> E[Signal Generation];
    E --> F[Order Execution];
    F --> G[Position Management];
    G --> H[Exit & Record];
```

### Layer Components

**🎯 Orchestration Layer**
- Bot Controller - Entry/exit logic, state management, kill switch

**📈 Processing Layer**
- Data Processor - Tick aggregation, candle formation, multi-timeframe sync

**📊 Indicator Layer**
- Calculations Engine - ATR, MACD, EMA, RSI, ADX, VWAP, Bollinger Bands

**🎲 Strategy Layer**
- Strategy Router - Signal generation, strategy selection

**🛡️ Risk Layer**
- Risk Engine - Position sizing, trailing stop, margin verification

**💾 Storage Layer**
- Data Cache - Historical data, intraday data, trade journal

**🔌 Connectivity Layer**
- WebSocket/REST Client - Real-time streaming, order placement

**📢 Alert Layer**
- Notification System - Trade events, errors, connection status

### Thread Safety
- `entry_lock` - Prevents overlapping entry signals
- `exit_lock` - Ensures atomic exit operations
- `threading.Lock()` for critical sections

---

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- Upstox API credentials (Client ID, API Key, Redirect URI)
- Upstox trading account

### Clone the Repository
```bash
git clone https://github.com/Omega-Xi/Algo-Trading.git
cd Algo-Trading
```
### Install Dependencies
```bash
pip install -r requirements.txt
```
## Dependencies
```text
upstox-client
pandas
numpy
pytz
python-dateutil
websocket-client
```
⚙ Configuration
1. Configure API Credentials
python
# configurations/trading_config.py
CONFIGURATION = {
    'client_id': 'YOUR_CLIENT_ID',
    'api_key': 'YOUR_API_KEY',
    'redirect_uri': 'YOUR_REDIRECT_URI',
    'access_token': None
}
2. Trading Parameters
Parameter	Default	Description
DRY_RUN	True	Paper trading mode
INTERVALS	["1","3","5","10","15"]	Candle timeframes
ATR_MULTIPLIER	1.5	Stop-loss distance
RISK_PERCENT	2.0	Risk per trade (%)
R_TO_R_RATIO	2.0	Risk-reward ratio
ENTRY_COOLDOWN	30	Seconds between trades
SL_ATR_TIMEFRAME	"5"	ATR calculation timeframe
3. Select Strategy
python
# strategies/__init__.py
STRATEGY_MAP = {
    "MACD EMA": macd_ema_strategy,      # ← Current active
    "MACD RSI": macd_rsi_strategy,
    "MACD ADX": macd_adx_strategy,
    "VWAP RSI": vwap_rsi_strategy,
    "Bollinger RSI": bollinger_rsi_mean_reversion,
    "Golden Strategy": golden_strategy
}

ACTIVE_STRATEGY = STRATEGY_MAP["MACD EMA"]
🚀 Usage
Dry Run Mode (Recommended First)
bash
python main.py
Live Trading Mode
Set DRY_RUN = False in configurations/trading_config.py

Ensure sufficient margin in your account

Run:

bash
python main.py
Bot Lifecycle Steps
Authentication: OAuth token generation

Data Preload: Load historical and intraday futures data

Market Sync: Wait for 15-minute mark

WebSocket Connection: Start streaming real-time data

Signal Generation: Strategy analysis on each candle

Order Execution: Place orders when signals trigger

Position Management: Monitor and update trailing stops

Exit: Close position on stop-loss or target hit

🛡 Risk Management
Position Sizing Formula
python
quantity = (available_margin * RISK_PERCENT/100) / (entry_price - trigger_price)
Trailing Stop Logic
python
def update_stop_loss(self):
    current_atr = self.candle_df['5']['atr'].iloc[-1]
    new_trigger = self.highest_price - (current_atr * ATR_MULTIPLIER)
    self.trigger_price = max(self.trigger_price, new_trigger)
Safety Mechanisms
Position validation before entry

Thread-safe operations with locks

Kill switch for emergency shutdown

Auto-reconnect for WebSocket

Cooldown period between trades

📊 Performance Reporting
python
# Trade history export
export_trades_to_csv(transcriber.trades)
# → trades_YYYYMMDD_HHMMSS.csv

# Performance report
generate_performance_report(transcriber)
# Includes: win rate, profit factor, Sharpe ratio, total P&L
Sample CSV Output
Timestamp	Symbol	Type	Entry Price	Exit Price	Quantity	P&L	Exit Reason
2025-03-20 10:15:00	NIFTY CE	BUY	125.50	140.25	75	+1106.25	TARGET_HIT
2025-03-20 11:30:00	NIFTY PE	BUY	98.75	85.00	100	-1375.00	STOPLOSS_HIT
🤝 Contributing
Fork the repository

Create a feature branch: git checkout -b feature/amazing-feature

Commit changes: git commit -m 'Add amazing feature'

Push: git push origin feature/amazing-feature

Open a Pull Request

Development Guidelines
Follow PEP 8 style guide

Add docstrings to new functions

Update README with new features

Test thoroughly in dry run mode

📝 License
text
MIT License

Copyright (c) 2025 Omega-Xi

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
⚠ Disclaimer
Trading involves significant risk of loss and is not suitable for all investors.

Past performance does not guarantee future results

This software is for educational purposes

Test thoroughly in dry run mode before live trading

The author is not responsible for any financial losses incurred

Always verify orders and monitor the bot during live trading

Use at your own risk

📞 Support & Contact
GitHub Issues: Report bugs or request features

Email: omega.xi@example.com

<div align="center">
Made with ❤️ by Omega-Xi

⭐ If this project helped you, please star the repository! ⭐

</div> ```