import pandas as pd
import logging
import os

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(filename)s:%(lineno)d | %(funcName)s() | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def export_trades_to_csv(trades, filename="trade_log.csv"):
    if not trades:
        logging.info("No trades to export.")
        return
    
    new_df = pd.DataFrame([t.__dict__ for t in trades])
    new_df = new_df.dropna(axis=1, how="all")  # drop empty columns
    
    if os.path.exists(filename):
        try:
            existing_df = pd.read_csv(filename)
            existing_df = existing_df.dropna(axis=1, how="all")
            combined_df = pd.concat([existing_df, new_df], ignore_index=True)
        except Exception as e:
            logging.error(f"Failed to read existing file: {e}")
            combined_df = new_df
    else:
        combined_df = new_df

    try:
        combined_df.to_csv(filename, index=False)
        logging.info(f"Trades appended successfully to '{filename}'")
    except Exception as e:
        logging.error(f"Failed to export trades: {e}")