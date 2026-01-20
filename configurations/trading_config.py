import upstox_client
from strategies.strategies import *
INTERVAL_MAP = {
    "1": "1min",
    "5": "5min",
    "10": "10min",
    "15": "15min"
}
STRATEGY_MAP={
    "MACD RSI":check_macd_rsi_signal
}
STRATEGY=STRATEGY_MAP["MACD RSI"]
CONFIGURATION=upstox_client.Configuration()
DRY_RUN_MARGIN=300000
DRY_RUN=True
TIME_UNIT="minutes"
INTERVALS=["1","5","10","15"]
SL_ATR_TIMEFRAME="15"
ENTRY_COOLDOWN = 30
ATR_MULTIPLIER=1.5
RSI_TRESHOLD_LOW=30
RSI_TRESHOLD_HIGH=70
RISK_PERCENT=2.0
R_TO_R_RATIO=2.0
API_VERSION = "2.0"