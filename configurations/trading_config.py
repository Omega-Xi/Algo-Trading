import upstox_client
from strategies.strategies import *

CONFIGURATION=upstox_client.Configuration()
DRY_RUN_MARGIN=323023.70
DRY_RUN=True
NAME="NIFTY"
MARKET_OPEN_TIME="09:15"
MARKET_CLOSE_TIME="15:30"
TIME_UNIT="minutes"
INTERVALS=["1","3","5","10","15"]
SL_ATR_TIMEFRAME="5"
ENTRY_COOLDOWN = 30
ATR_MULTIPLIER=1.5
RISK_PERCENT=2.0
R_TO_R_RATIO=2.0
API_VERSION = "2.0"
INTERVAL_MAP = {
    "1": "1min",
    "3": "3min",
    "5": "5min",
    "10": "10min",
    "15": "15min"
}
STRATEGY_MAP={
    "MACD EMA":macd_ema_strategy,
    "MACD RSI":macd_rsi_strategy,
    "MACD ADX":macd_adx_strategy,
    "VWAP RSI":vwap_rsi_strategy,
    "BOLLINGER RSI":bollinger_rsi_mean_reversion,
    "DI ADX":di_adx_strategy,
    "GOLDEN STRATEGY":golden_strategy
}
STRATEGY=STRATEGY_MAP["MACD EMA"]