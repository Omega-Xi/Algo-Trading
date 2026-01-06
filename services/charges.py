def calculate_charges(entry_price, exit_price, quantity, product_type="intraday", brokerage_fee=30):
    turnover = (entry_price + exit_price) * quantity
    buy_value = entry_price * quantity
    sell_value = exit_price * quantity

    brokerage = brokerage_fee * 2
    stt = {
        "delivery": 0.001 * (buy_value + sell_value),
        "intraday": 0.00025 * sell_value,
        "futures": 0.000125 * sell_value,
        "options": 0.000625 * sell_value
    }.get(product_type, 0)

    txn_charges = 0.0000325 * turnover
    sebi_fees = 0.000001 * turnover
    stamp_duty = {
        "delivery": 0.00015 * buy_value,
        "intraday": 0.00003 * buy_value,
        "futures": 0.00002 * buy_value,
        "options": 0.00003 * buy_value
    }.get(product_type, 0)

    gst = 0.18 * (brokerage + txn_charges)
    total_charges = brokerage + stt + txn_charges + sebi_fees + stamp_duty + gst

    return total_charges