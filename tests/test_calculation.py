from calculations import calculations
import logging
from configurations import trading_config
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(filename)s:%(lineno)d | %(funcName)s() | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

TEST_LOT_SIZE=35
TEST_OPTION_PRICE=600
TEST_OPTION_DELTA=0.5
TEST_MARGIN=300000
TEST_ATR=1

# Example synthetic OHLC data
data = {
    "open":  [100, 102, 101, 103, 104, 105, 106, 107],
    "high":  [103, 104, 103, 105, 106, 107, 108, 109],
    "low":   [99, 101, 100, 102, 103, 104, 105, 106],
    "close": [102, 103, 102, 104, 105, 106, 107, 108],
    "volume":[1500, 1600, 1550, 1650, 1700, 1750, 1800, 1850]
}
df = pd.DataFrame(data)

# Add timestamps: first 4 rows = Day 1, next 4 rows = Day 2
df["timestamp"] = pd.date_range("2024-01-01 09:15", periods=8, freq="5min")
df.loc[4:, "timestamp"] = pd.date_range("2024-01-02 09:15", periods=4, freq="5min")

df.set_index("timestamp", inplace=True)


if __name__=="__main__":
    # Check Trigger Price Calculation 
    trigger_price=calculations.calculate_trigger_price(TEST_ATR,TEST_OPTION_PRICE, TEST_OPTION_DELTA)
    if trigger_price is None:
        logging.critical("Failed To Calculate Trigger Price Using ATR")
    else:
        logging.info(f"Trigger Price Calculation Using ATR Succesfull :{trigger_price}")

    # Check Quantity Calculation
    quantity=calculations.calculate_quantity(TEST_LOT_SIZE,TEST_OPTION_PRICE,TEST_MARGIN,trigger_price)
    if quantity is None:
        logging.critical("Failed To Calculate Quantity")
    elif quantity==0 :
        logging.warning("Margin Too Low")
    else:
        logging.info(f"Quantity Calculation Succesfull :{quantity}")

    # Check Exit Price
    exit_price=calculations.calculate_exit_price(TEST_OPTION_PRICE,trigger_price)
    if exit_price is None:
        logging.critical("Failed to Calculate Exit Price")
    else:
        logging.info(f"Exit Price Calculation Succesfull :{exit_price}")

    # Calculate all indicators
    df_with_indicators = calculations.calculate_indicators(df)
    indicator_cols = [
        "ema12", "ema26", "macd", "signal",
        "rsi", "atr", "plus_di", "minus_di",
        "dx", "adx" , "vwap"
    ]
    print(df_with_indicators[indicator_cols])