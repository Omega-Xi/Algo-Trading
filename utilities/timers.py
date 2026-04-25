import pandas as pd
from datetime import datetime
import pytz
from configurations.trading_config import MARKET_CLOSE_TIME,MARKET_OPEN_TIME, TRADE_END_TIME , TRADE_START_TIME
class Timer:
    @staticmethod
    def is_n_min_mark(ts, interval_in_minutes, tolerance=2):
        """
        Check if timestamp `ts` is within `tolerance` seconds of an n-minute boundary.
        """
        boundary_minute = (ts.minute // interval_in_minutes) * interval_in_minutes
        boundary = ts.replace(minute=boundary_minute, second=0, microsecond=0)
        return 0 <= (ts - boundary).total_seconds() <= tolerance
    
    @staticmethod
    def market_is_open():
        now_aware = datetime.now(pytz.timezone('Asia/Kolkata'))
        current_time = now_aware.time()
        if current_time < pd.to_datetime(MARKET_OPEN_TIME).time() or current_time > pd.to_datetime(MARKET_CLOSE_TIME).time():
            return False
        else:
            return True
        
    @staticmethod
    def is_time_to_trade():
        now_aware = datetime.now(pytz.timezone('Asia/Kolkata'))
        current_time = now_aware.time()
        if current_time < pd.to_datetime(TRADE_START_TIME).time() or current_time > pd.to_datetime(TRADE_END_TIME).time():
            return False
        else:
            return True
