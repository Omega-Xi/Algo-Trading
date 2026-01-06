import logging
from configutarions import trading_config
import numpy as np

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(filename)s:%(lineno)d | %(funcName)s() | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def calculate_quantity(lot_size,option_price,available_margin):
    if option_price <= 0:
        logging.error("Invalid option price for quantity calculation")
        return 0
    usable_margin=(trading_config.MARGIN_PERCENT)*available_margin
    max_lots=usable_margin//(option_price*lot_size)
    quantity=int(max_lots)*lot_size
    return max(quantity, 0)

def calculate_trigger_price( quantity, current_atr=None, option_price=None, use_atr=True):
    if quantity <= 0 or option_price is None:
        return 0
    if use_atr and current_atr is not None:
        # Dynamic stop based on ATR
        atr_stop = current_atr * trading_config.ATR_MULTIPLIER
        trigger_price = option_price - atr_stop
    else:
        # Fall back
        adjusted_risk_percentage = max(trading_config.RISK_PERCENT, 2)
        trigger_price = option_price * (1 - adjusted_risk_percentage)
    # Apply min/max bounds
    min_stop = option_price * (1 - trading_config.MINIMUM_SL_PERCENT/100)
    max_stop = option_price * (1 - trading_config.MAXIMUM_SL_PERCENT/100)
    trigger_price = max(trigger_price, min_stop)  # Not too tight
    trigger_price = min(trigger_price, max_stop)  # Not too loose
    
    return round(max(trigger_price, 0.05), 2)

def calculate_indicators(candle_df):
    # --- MACD Calculation ---
    df = candle_df.copy()
    df["ema12"] = df["close"].ewm(span=12,adjust=False).mean()
    df["ema26"] = df["close"].ewm(span=26,adjust=False).mean()
    df["macd"] = df["ema12"] - df["ema26"]
    df["signal"] = df["macd"].ewm(span=9,adjust=False).mean()

    # --- RSI Calculation ---
    delta = df["close"].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.ewm(alpha=1/14, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/14, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    df["rsi"] = 100 - (100 / (1 + rs))

    # --- ATR Calculation (RMA) ---
    df['high_low']   = df['high'] - df['low']
    df['high_close'] = (df['high'] - df['close'].shift()).abs()
    df['low_close']  = (df['low'] - df['close'].shift()).abs()
    df['tr']         = df[['high_low', 'high_close', 'low_close']].max(axis=1)
    df['atr'] = df['tr'].ewm(alpha=1/14, adjust=False).mean()

    # --- Directional Movement ---
    up_move   = df['high'].diff()
    down_move = -df['low'].diff()

    df['plus_dm']  = np.where((up_move > down_move) & (up_move > 0), up_move, 0.0)
    df['minus_dm'] = np.where((down_move > up_move) & (down_move > 0), down_move, 0.0)

    # --- DI using RMA ---
    plus_dm_rma  = df['plus_dm'].ewm(alpha=1/14, adjust=False).mean()
    minus_dm_rma = df['minus_dm'].ewm(alpha=1/14, adjust=False).mean()

    df['plus_di']  = 100 * (plus_dm_rma / df['atr'])
    df['minus_di'] = 100 * (minus_dm_rma / df['atr'])

    # --- DX and ADX (RMA) ---
    df['dx'] = 100 * (abs(df['plus_di'] - df['minus_di']) / (df['plus_di'] + df['minus_di']))
    df['dx'] = df['dx'].fillna(0) 
    df['adx'] = df['dx'].ewm(alpha=1/14, adjust=False).mean()

    return df