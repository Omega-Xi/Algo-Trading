from services.charges import calculate_charges
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

class Transcriber:
    def __init__(self, initial_margin):
        self.trades = []
        self.position = None
        self.initial_balance = initial_margin
        self.current_balance = initial_margin

    def record_entry(self, trade):
        self.trades.append(trade)
        self.position = trade.type
        logging.info(f"Trade entered: {trade.type} at {trade.entry_price}, Time: {trade.entry_time.strftime("%H:%M:%S")}")

    def record_exit(self, exit_price, exit_reason, timestamp):
        active_trade = next((t for t in reversed(self.trades) if t.status == "ACTIVE"), None)
        if not active_trade:
            logging.info("No active trade to exit")
            return

        active_trade.exit_time = timestamp
        active_trade.exit_price = exit_price
        active_trade.status = "CLOSED"
        active_trade.exit_reason = exit_reason

        charges = calculate_charges(active_trade.entry_price, exit_price, active_trade.quantity, product_type="intraday")
        gross_pnl = (exit_price - active_trade.entry_price) * active_trade.quantity
        net_pnl = gross_pnl - charges

        active_trade.gross_pnl = gross_pnl
        active_trade.net_pnl = net_pnl
        active_trade.charges = charges
        active_trade.pnl = net_pnl

        self.current_balance += net_pnl
        logging.info(f"Trade exited: {active_trade.type} at {exit_price}, Time: {timestamp.strftime("%H:%M:%S")}, Net P&L: {net_pnl:.2f}")

        self.position = None