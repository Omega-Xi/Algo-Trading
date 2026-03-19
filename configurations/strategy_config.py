STRTEGY_CONFIG={
    "ADX_TRESHOLD": 25,
    "RSI_TRESHOLD_LOW": 30,
    "RSI_TRESHOLD_HIGH": 70,
    "RSI_TRESHOLD_MID": 50,
    "VWAP_CLOSE_TOLERANCE": 0.00001
}

def get_strategy_config():
    return STRTEGY_CONFIG

def update_strategy_config(new_config: dict):
    STRTEGY_CONFIG.update(new_config)