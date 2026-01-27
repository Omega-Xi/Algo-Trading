import upstox_client
from strategies.strategies import *

CONFIGURATION=upstox_client.Configuration()
DRY_RUN_MARGIN=300000
DRY_RUN=True
TIME_UNIT="minutes"
INTERVALS=["1","5","10","15"]
SL_ATR_TIMEFRAME="5"
ENTRY_COOLDOWN = 30
ATR_MULTIPLIER=1.5
RISK_PERCENT=2.0
R_TO_R_RATIO=2.0
API_VERSION = "2.0"
INTERVAL_MAP = {
    "1": "1min",
    "5": "5min",
    "10": "10min",
    "15": "15min"
}
STRATEGY_MAP={
    "MACD RSI":macd_rsi_strategy,
    "MACD ADX":macd_adx_strategy
}
STRATEGY=STRATEGY_MAP["MACD RSI"]