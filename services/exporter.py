import pandas as pd
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(filename)s:%(lineno)d | %(funcName)s() | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def export_trades_to_excel(trades, filename="trade_log.csv"):
    if not trades:
        logging.info("No trades to export.")
        return
    
    df = pd.DataFrame([t.__dict__ for t in trades])
    df.to_csv(filename, index=False)
    logging.info(f"Trade log successfully exported to '{filename}'")