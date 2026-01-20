import pandas as pd
import logging
import math
from configurations.trading_config import INTERVAL_MAP

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(filename)s:%(lineno)d | %(funcName)s() | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

class Data_Processor:
    def __init__(self):
        self.get_instruments()
        self.expiry_date=None
        self.instrument_key=None
        self.option_key=None

    def get_instruments(self):
        self.instruments=pd.read_json("https://assets.upstox.com/market-quote/instruments/exchange/NSE.json.gz")
        self.instruments['expiry']=pd.to_datetime(self.instruments['expiry'],unit='ms',errors='coerce')
        self.instruments['expiry']=self.instruments['expiry'].dt.date
        self.instruments['expiry']=pd.to_datetime(self.instruments['expiry'])
        logging.info("Loaded Instrument Data")
        
    @staticmethod
    def convert_to_df(response):
        df = pd.DataFrame(response.data.candles, columns=["timestamp","open","high","low","close","volume","open_interest"])
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df.set_index("timestamp", inplace=True)
        if df.index.tz is None:
            df.index = df.index.tz_localize("UTC")
            df.index = df.index.tz_convert("Asia/Kolkata")
        else:
            df.index = df.index.tz_convert("Asia/Kolkata")
        df.sort_index(inplace=True)
        return df
    
    @staticmethod
    def convert_to_candles(df,interval,historic_df,intraday_df):
        time_frame=INTERVAL_MAP[interval]
        resampled = df["price"].resample(time_frame).ohlc().dropna()
        frames = [historic_df, intraday_df, resampled]
        frames = [df for df in frames if not df.empty]   # exclude empties
        candle_df = pd.concat(frames) if frames else pd.DataFrame()
        # Remove duplicate index values 
        candle_df = candle_df[~candle_df.index.duplicated(keep='last')]
        return candle_df

    def get_instrument_key(self,name):
        self.name=name
        filtered=self.instruments[self.instruments['trading_symbol']==self.name]['instrument_key']
        if filtered.empty:
            logging.warning("Instrument Key Not Found")
            return None
        self.instrument_key=filtered.squeeze()
        logging.info(f"Instrument Key: {self.instrument_key}")
        return self.instrument_key
    
    def get_lot_size(self):
        futures = self.instruments[
            (self.instruments['segment'] == "NSE_FO") &
            (self.instruments['underlying_symbol'] == self.name)
        ]
        futures_sorted = futures.sort_values(by='expiry')
        if not futures_sorted.empty:
            lot_size=int(futures_sorted.iloc[0]['lot_size'])
            logging.info(f"Lot Size For {self.name} :{lot_size}")
            return lot_size
        else:
            logging.warning(f"No Futures Found For Instrument: {self.name}")
            return None
        
    def get_expiry_date(self):
        try:
            instruments=self.instruments[self.instruments['name']==self.name]
            instruments_sorted = instruments.sort_values(by='expiry')
            first_expiry = instruments_sorted['expiry'].dropna().sort_values().iloc[0]
            first_expiry = first_expiry.strftime('%Y-%m-%d')
            self.expiry_date=first_expiry
            logging.info(f"Expiry Date :{self.expiry_date}")
            return self.expiry_date
        except Exception as e:
            logging.error(f"Unable To Fetch Expiry : {e}")
            return None

    def get_option_key(self,order_type,index_price):
        if index_price is None:
            logging.warning("Index price not available for option key calculation")
            return None
        if order_type == 'CE':
            strike_price = math.floor(index_price / 100) * 100
        else:
            strike_price = math.ceil(index_price / 100) * 100
        # Convert expiry_date to datetime for comparison
        self.expiry_date = pd.to_datetime(self.expiry_date)
        option_key = self.instruments[
            (self.instruments['instrument_type'] == order_type) &
            (self.instruments['name'] == self.name) &
            (self.instruments['expiry'] == self.expiry_date) &
            (self.instruments['strike_price'] == strike_price)
        ]['instrument_key']
        if option_key.empty:
            logging.critical(f"Option key not found for {order_type}, {self.name}, {self.expiry_date}, {strike_price}")
            return None
        self.option_key=option_key.squeeze()
        return self.option_key