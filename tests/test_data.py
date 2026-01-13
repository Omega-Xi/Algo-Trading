import logging
from data.data_collector import Data_Collector
from data.data_processor import Data_Processor
from authenticator.upstox_authenticator import Authenticator

TEST_INDEX_PRICE=60000
INSTRUMENT_NAME="BANKNIFTY"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(filename)s:%(lineno)d | %(funcName)s() | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

if __name__=="__main__":
    authenticator=Authenticator()
    access_token=authenticator.get_access_token()
    data_collector=Data_Collector(access_token,dry_run=True)
    data_processor=Data_Processor(INSTRUMENT_NAME)

    # Check Margin
    margin=data_collector.get_margin()
    if margin is None:
        logging.critical("Margin Fetching Failed")
    else:
        logging.info(f"Margin Fetching Succesfull :{margin}")

    # Check Instrument Key
    instrument_key=data_processor.get_instrument_key()
    if instrument_key is None:
        logging.critical("Failed to Extract Instrument key")
    else:
        logging.info(f"Instrument Key Extraction Succesfull :{instrument_key}")

    # Check Lot Size
    lot_size=data_processor.get_lot_size()
    if lot_size is None:
        logging.critical("Failed to Fetch Lot Size")
    else:
        logging.info(f"Lot Size Fetching Succesfull :{lot_size}")

    # Check Historic Data
    if data_collector.get_historic_data(instrument_key) is None:
        logging.critical("Failed to Fetch Historical Data")
    else:
        logging.info("Historic Data Fetching Succesfull")

    # Check Intraday Data
    if data_collector.get_intraday_data(instrument_key) is None:
        logging.critical("Failed to Fetch Intraday Data")
    else:
        logging.info("Intraday Data Fetching Succesfull")

    # Check Expiry
    expiry_date=data_processor.get_expiry_date()
    if expiry_date is None:
        logging.critical("Failed to Fetch Expiry")
    else:
        logging.info(f"Expiry Fetching Succesfull :{expiry_date}")

    # Check Option Key
    option_key=data_processor.get_option_key("CE",TEST_INDEX_PRICE)
    if option_key is None:
        logging.critical("Failed to Extract Option Key")
    else:
        logging.info(f"Option Key Extraction Succesfull :{option_key}")

    # Check Option Price
    option_price=data_collector.get_option_price(option_key)
    if option_price is None:
        logging.critical("Failed to Fetch Option Price")
    else:
        logging.info(f"Option Price Fetching Succesfull :{option_price}")
    
    # Check Active Positions
    position_active=data_collector.check_position()
    if position_active is None:
        logging.critical("Failed to Check Position")
    else:
        logging.info(f"Position Check Succesfull | Position Status :{position_active}")