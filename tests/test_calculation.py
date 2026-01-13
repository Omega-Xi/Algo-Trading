from calculations import calculations
import logging
from configurations import trading_config

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