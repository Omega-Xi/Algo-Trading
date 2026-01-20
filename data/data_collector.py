import logging
import upstox_client
from upstox_client.rest import ApiException
from data.data_processor import Data_Processor
from configurations import trading_config
from datetime import date,timedelta

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(filename)s:%(lineno)d | %(funcName)s() | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

class Data_Collector:
    def __init__(self,access_token,dry_run):
        self.access_token=access_token
        trading_config.CONFIGURATION = upstox_client.Configuration()
        trading_config.CONFIGURATION.access_token = self.access_token
        self.dry_run=dry_run
        self.option_price=None
        self.available_margin=None

    def get_margin(self):
        if self.dry_run:
            self.available_margin=trading_config.DRY_RUN_MARGIN
            logging.info("Dry Run Margin Fetched")
            return self.available_margin
        api_instance = upstox_client.UserApi(upstox_client.ApiClient(trading_config.CONFIGURATION))
        try:
            # Get User Fund And Margin
            api_response = api_instance.get_user_fund_margin(trading_config.API_VERSION)
            self.available_margin=api_response.data['equity'].available_margin
            logging.info("Margin Fetched Successfully")
            return self.available_margin
        except ApiException as e:
            logging.error(f"Exception while fetching margin :{e}")
            return None

    def get_historic_data(self,instrument_key):
        today=date.today()
        previous_day=today-timedelta(days=7)
        str_today=str(today)
        str_previous_day=str(previous_day)
        apiInstance = upstox_client.HistoryV3Api(upstox_client.ApiClient(trading_config.CONFIGURATION))
        try:
            dfs=[]
            for interval in trading_config.INTERVALS:
                df=Data_Processor.convert_to_df(
                    apiInstance.get_historical_candle_data1(instrument_key, trading_config.TIME_UNIT, interval, str_today, str_previous_day)
                )
                dfs.append(df)
            return tuple(dfs)
        except Exception as e:
            logging.error(f"Exception while fetching Historic Data :{e}")
            return None

    def get_intraday_data(self,instrument_key):
        api_instance = upstox_client.HistoryV3Api(upstox_client.ApiClient(trading_config.CONFIGURATION))
        try:
            dfs=[]
            for interval in trading_config.INTERVALS:
                df=Data_Processor.convert_to_df(
                    api_instance.get_intra_day_candle_data(instrument_key, trading_config.TIME_UNIT, interval)
                )
                dfs.append(df)
            return tuple(dfs)
        except Exception as e:
            logging.error(f"Exception while fetching Intraday Data :{e}")
            return None

    def get_option_price(self,option_key):
        if option_key is None:
            logging.error("Invalid option key")
            return None
        trading_config.CONFIGURATION.access_token = self.access_token
        api_instance = upstox_client.MarketQuoteV3Api(upstox_client.ApiClient(trading_config.CONFIGURATION))
        try:
            response = api_instance.get_ltp(instrument_key=option_key)
            last_trade_price = response.data[next(iter(response.data))].last_price
            if last_trade_price:
                self.option_price=last_trade_price
                logging.info(f"Option Price :{self.option_price}")
                return self.option_price
            else:
                logging.warning("No candle data available.")
                return None
        except ApiException as e:
            logging.error(f"API Exception: {e}")
            return None
        except Exception as e:
            logging.error(f"Exception when fetching option price: {e}")
            return None
        
    def check_position(self):
        api_instance = upstox_client.PortfolioApi(upstox_client.ApiClient(trading_config.CONFIGURATION))
        try:
            api_response = api_instance.get_positions(trading_config.API_VERSION)
            return bool(api_response.data)
        except ApiException as e:
            logging.error(f"Exception when fetching position data :{e}")
            return None

    # Intruments are fetched in Data_Processor class for easier accessibility