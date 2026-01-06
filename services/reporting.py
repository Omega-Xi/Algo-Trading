import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(filename)s:%(lineno)d | %(funcName)s() | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def generate_performance_report(transcriber):
    trades = transcriber.trades
    closed_trades = [t for t in trades if t.status == "CLOSED"]
    active_trades = [t for t in trades if t.status == "ACTIVE"]

    print("\n" + "="*60)
    print("FINAL TRADING PERFORMANCE REPORT")
    print("="*60)

    if active_trades:
        logging.info(f"\nACTIVE TRADES: {len(active_trades)}")
        for t in active_trades:
            print(f"Trade {t.trade_id}: {t.type} | Entry: {t.entry_price} | Qty: {t.quantity} | Target: {t.target_price}")

    if closed_trades:
        total_pnl = sum(t.pnl for t in closed_trades)
        logging.info(f"\nCLOSED TRADES PERFORMANCE:")
        print(f"Initial Balance: ₹{transcriber.initial_balance:.2f}")
        print(f"Final Balance:   ₹{transcriber.current_balance:.2f}")
        print(f"Total P&L:       ₹{total_pnl:.2f}")
    else:
        logging.info("\nNo closed trades to analyze")

    print("="*60)