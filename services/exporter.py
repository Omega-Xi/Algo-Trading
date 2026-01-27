import pandas as pd
import logging
import os

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(filename)s:%(lineno)d | %(funcName)s() | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def export_trades_to_excel(trades, filename="trade_log.xlsx"):
    if not trades:
        logging.info("No trades to export.")
        return
    
    new_df = pd.DataFrame([t.__dict__ for t in trades])
    new_df = new_df.dropna(axis=1, how="all")  # drop empty columns
    
    if os.path.exists(filename):
        try:
            existing_df = pd.read_excel(filename)
            existing_df = existing_df.dropna(axis=1, how="all")
            combined_df = pd.concat([existing_df, new_df], ignore_index=True)
        except Exception as e:
            logging.error(f"Failed to read existing file: {e}")
            combined_df = new_df
    else:
        combined_df = new_df
    
    # Make datetimes timezone-naive
    for col in combined_df.select_dtypes(include=["datetimetz"]).columns:
        combined_df[col] = combined_df[col].dt.tz_localize(None)
    
    try:
        combined_df.to_excel(filename, index=False)
        logging.info(f"Trades appended successfully to '{filename}'")
    except Exception as e:
        logging.error(f"Failed to export trades: {e}")