import logging
from configurations import trading_config
import numpy as np
import math

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(filename)s:%(lineno)d | %(funcName)s() | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def calculate_trigger_price(current_atr=None, option_price=None, option_delta=0.5):
    if option_price is None:
        logging.error("Option Price not available")
        return None
    if current_atr is None:
        logging.error("ATR not available")
        return None
    atr_stop = current_atr * trading_config.ATR_MULTIPLIER * option_delta
    trigger_price = option_price - atr_stop
    return round(trigger_price, 2)

def calculate_quantity(lot_size, option_price, available_margin, trigger_price):
    if option_price <= 0 or trigger_price is None:
        logging.error("Invalid Price Data")
        return None
    risk_per_lot=(option_price-trigger_price)*lot_size
    if risk_per_lot <=0:
        logging.error("Risk per lot is negative")
        return None
    max_risk=available_margin * trading_config.RISK_PERCENT/100
    max_lots_by_risk=int(max_risk//risk_per_lot)
    max_lots_by_margin=int(available_margin//(option_price*lot_size))
    final_lots = min(max_lots_by_risk, max_lots_by_margin)
    quantity=final_lots*lot_size
    return max(quantity, 0)

def calculate_exit_price(option_price,trigger_price):
    if option_price is None or trigger_price is None:
        logging.info("Invalid Price Data")
        return None
    exit_price=math.floor(option_price + (option_price - trigger_price) * trading_config.R_TO_R_RATIO)
    return exit_price

# --- MACD Calculation ---
def caculate_macd(candle_df):
    df = candle_df.copy()
    df["ema12"] = df["close"].ewm(span=12,adjust=False).mean()
    df["ema26"] = df["close"].ewm(span=26,adjust=False).mean()
    df["macd"] = df["ema12"] - df["ema26"]
    df["signal"] = df["macd"].ewm(span=9,adjust=False).mean()
    return df

# --- RSI Calculation ---
def calculate_rsi(df):
    delta = df["close"].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.ewm(alpha=1/14, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/14, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    df["rsi"] = 100 - (100 / (1 + rs.fillna(0)))
    return df

# --- ATR Calculation (RMA) ---
def calculate_atr(df):
    df['high_low']   = df['high'] - df['low']
    df['high_close'] = (df['high'] - df['close'].shift()).abs()
    df['low_close']  = (df['low'] - df['close'].shift()).abs()
    df['tr']         = df[['high_low', 'high_close', 'low_close']].max(axis=1)
    df['atr'] = df['tr'].ewm(alpha=1/14, adjust=False).mean()
    return df

# --- DX and ADX (RMA) ---
def calculate_adx(df):
    if 'atr' not in df.columns:
        df = calculate_atr(df)
    up_move   = df['high'].diff()
    down_move = -df['low'].diff()
    df['plus_dm']  = np.where((up_move > down_move) & (up_move > 0), up_move, 0.0)
    df['minus_dm'] = np.where((down_move > up_move) & (down_move > 0), down_move, 0.0)
    plus_dm_rma  = df['plus_dm'].ewm(alpha=1/14, adjust=False).mean()
    minus_dm_rma = df['minus_dm'].ewm(alpha=1/14, adjust=False).mean()
    df['plus_di']  = 100 * (plus_dm_rma / df['atr'])
    df['minus_di'] = 100 * (minus_dm_rma / df['atr'])
    df['dx'] = 100 * (abs(df['plus_di'] - df['minus_di']) / (df['plus_di'] + df['minus_di']))
    df['dx'] = df['dx'].fillna(0) 
    df['adx'] = df['dx'].ewm(alpha=1/14, adjust=False).mean()
    return df

def calculate_indicators(candle_df):
    df=caculate_macd(candle_df)
    df=calculate_rsi(df)
    df=calculate_atr(df)
    df=calculate_adx(df)
    return df