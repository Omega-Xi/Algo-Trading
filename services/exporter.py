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
    for col in combined_df.columns:
        if pd.api.types.is_datetime64_any_dtype(combined_df[col]):
            # Strip timezone if present
            if hasattr(combined_df[col].dt, "tz"):
                combined_df[col] = combined_df[col].dt.tz_localize(None)
        else:
            # Try coercing object columns to datetime
            try:
                combined_df[col] = pd.to_datetime(combined_df[col], errors="ignore")
                if pd.api.types.is_datetime64_any_dtype(combined_df[col]) and hasattr(combined_df[col].dt, "tz"):
                    combined_df[col] = combined_df[col].dt.tz_localize(None)
            except Exception:
                pass
    
    combined_df = combined_df.drop_duplicates()

    try:
        combined_df.to_excel(filename, index=False)
        logging.info(f"Trades appended successfully to '{filename}'")
    except Exception as e:
        logging.error(f"Failed to export trades: {e}")