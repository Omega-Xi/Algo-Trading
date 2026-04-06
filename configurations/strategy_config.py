STRATEGY_CONFIG={
    "ADX_TRESHOLD": 25,
    "ER_TRESHOLD": 0.35,
    "RSI_TRESHOLD_LOW": 30,
    "RSI_TRESHOLD_HIGH": 70,
    "RSI_TRESHOLD_MID": 50,
    "VWAP_CLOSE_TOLERANCE": 0.00001
}

def get_strategy_config():
    return STRATEGY_CONFIG

def update_strategy_config(new_config: dict):
    STRATEGY_CONFIG.update(new_config)