import upstox_client
from upstox_client import MarketDataStreamerV3
from upstox_client.rest import ApiException
from configurations.trading_config import *
from authenticator.upstox_authenticator import Authenticator
from utilities.alerts import Alerts
from data.data_processor import Data_Processor
from data.data_collector import Data_Collector
from models.transcriber import Transcriber
from models.trade_record import Trade
from calculations import calculations
from strategies import strategies
from datetime import datetime
import pandas as pd
import threading
import pytz
import logging
import math

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(filename)s:%(lineno)d | %(funcName)s() | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

class Bot:
    def __init__(self):
        self.authenticator=Authenticator()
        self.access_token=self.authenticator.get_access_token()
        self.data_processor=Data_Processor()
        self.data_collector=Data_Collector(self.access_token,DRY_RUN)
        self.kill_switch=False
        self.position_active=False
        self.status="OFFLINE"
        self.tick_buffer = []
        self.candle_df={}
        self.historic_df={}
        self.intraday_df={}
        self.entry_lock=threading.Lock()
        self.exit_lock=threading.Lock()
        self.option_type=None
        self.option_key=None
        self.index_price=None
        self.option_price=None
        self.trigger_price=None
        self.exit_price=None
        self.latest_entry_time=None
        self.last_exit_time = None
        self.streamer=None
        self.available_margin=None
        self.name=None
        self.lot_size=None
        self.main_instrument_key=None
        self.expiry_date=None

    def can_enter_trade(self):    
        if self.last_exit_time is None:
            return True
        now_aware = datetime.now(pytz.timezone('Asia/Kolkata'))
        elapsed = (now_aware - self.last_exit_time).total_seconds()
        return elapsed >= ENTRY_COOLDOWN
    
    def launch(self):
        self.name=input("Instrument Name :")
        self.available_margin=self.data_collector.get_margin()
        self.transcriber=Transcriber(self.available_margin)
        self.main_instrument_key=self.data_processor.get_instrument_key(self.name)
        self.lot_size=self.data_processor.get_lot_size()
        self.expiry_date=self.data_processor.get_expiry_date()
        historic_dfs=self.data_collector.get_historic_data(self.main_instrument_key)
        if historic_dfs is None:
            logging.critical("Historical Data unavailable. Bot cannot launch safely")
            Alerts.error()
            self.status="ERROR"
            return
        else:
            logging.info("Fetched Historic Data")
            self.historic_df=dict(zip(INTERVALS, historic_dfs))
        intraday_dfs=self.data_collector.get_intraday_data(self.main_instrument_key)
        if intraday_dfs is None:
            logging.critical("Intraday Data unavailable. Bot cannot launch safely")
            Alerts.error()
            self.status="ERROR"
            return
        else:
            logging.info("Fetched Intraday Data")
            self.intraday_df=dict(zip(INTERVALS,intraday_dfs))
        self.start_connection()
    
    def start_connection(self):
        CONFIGURATION.access_token=self.access_token
        self.streamer = MarketDataStreamerV3(
            upstox_client.ApiClient(CONFIGURATION),
            [self.main_instrument_key],  # Only subscribe to main instrument initially
            mode="full"
        )
        self.streamer.auto_reconnect(True, 5, 3)
        self.streamer.on("open",self.on_open)
        self.streamer.on("message", self.on_message)
        self.streamer.on("error", self.on_error)
        self.streamer.on("close", self.on_close)
        self.streamer.connect()

    def on_open(self):
        logging.info("Websocket Connection Established")
        self.status="ONLINE"
        Alerts.websocket_connected()

    def on_error(self,error):
        logging.error(f"Websocket Error :{error}")
        self.status="ERROR"
        Alerts.websocket_error()

    def on_close(self,*args):
        logging.info("Websocket Disconnected")
        self.status="OFFLINE"
        Alerts.websocket_disconnected()

    def on_message(self,message):
        if self.kill_switch:
            logging.warning("Kill Switch Active. Ignoring Incoming Messages")
            return    
        if "feeds" not in message or not message["feeds"]:
            logging.warning("No Feed Data Aailable")
            return
        data = message["feeds"]
        feed_timestamp = pd.to_datetime(int(message['currentTs']),unit='ms').tz_localize('UTC').tz_convert('Asia/Kolkata')

        for instrument_key, feed_data in data.items():
            try:
                if instrument_key == self.main_instrument_key:
                    #Analyze index data
                    ltp = feed_data['fullFeed']['indexFF']['ltpc']['ltp']
                    self.index_price = ltp
                    self.tick_buffer.append({"timestamp": feed_timestamp, "price": ltp})
                    self.aggregate_candles()
                if self.exit_lock.acquire(blocking=False):
                    try:
                        # check for exit conditions
                        if hasattr(self, 'option_key') and instrument_key == self.option_key and self.position_active and feed_timestamp>(self.latest_entry_time + pd.Timedelta(seconds=1)):
                            ltp = feed_data['fullFeed']['marketFF']['ltpc']['ltp']
                            timestamp = pd.to_datetime(int(message['currentTs']), unit='ms').tz_localize('UTC').tz_convert('Asia/Kolkata')

                            if not DRY_RUN:
                                self.position_active = self.data_collector.check_position()
                                if not self.position_active:
                                    logging.info(f"Stop loss hit: {ltp} <= {self.trigger_price}, position exited via SL-M.")
                                    self.transcriber.record_exit(ltp, "STOPLOSS_HIT", timestamp)
                                    self._cleanup_after_exit()
                                    Alerts.trade_exited()
                                    return

                            if ltp <= self.trigger_price:
                                logging.info(f"Stop loss hit: {ltp} <= {self.trigger_price}, position exited via SL-M.")
                                self.transcriber.record_exit(ltp, "STOPLOSS_HIT", timestamp)
                                self._cleanup_after_exit()
                                return

                            if ltp >= self.exit_price:
                                print(f"Target reached: {ltp} >= {self.exit_price}, exiting position.")
                                self.transcriber.record_exit(ltp, "TARGET_HIT", timestamp)
                                if not DRY_RUN:
                                    self.exit_position()
                                self._cleanup_after_exit()
                                return
                    finally:
                        self.exit_lock.release()
                else:
                    logging.info("Exit lock busy, Skipping exit check")
            except KeyError as e:
                Alerts.error()
                logging.error(f"Data access error: {e} - possibly unexpected data structure")
            except Exception as e:
                Alerts.error()
                logging.error(f"Unexpected error: {e}")

    def aggregate_candles(self):
        df = pd.DataFrame(self.tick_buffer)
        if df.empty:
            return
        df.set_index("timestamp", inplace=True)
        df = df.between_time("09:15", "15:30")
        for interval in INTERVALS:
            historic = self.historic_df.get(interval)
            intraday = self.intraday_df.get(interval)
            self.candle_df[interval] = self.data_processor.convert_to_candles(df, interval, historic, intraday)
            self.candle_df[interval] = calculations.calculate_indicators(self.candle_df[interval])

        if self.entry_lock.acquire(blocking=False):
            try:
                STRATEGY(self,self.candle_df)
            finally:
                self.entry_lock.release()
        else:
            logging.info("Entry lock busy, Skipping signal check")

    def enter_trade(self,option_type):
        if self.position_active:
            logging.info("Trade Active,Skipping Entries")
            return
        self.option_key=self.data_processor.get_option_key(option_type,self.index_price)
        if self.option_key is None:
            logging.warning(f"Could not find option key for {option_type}")
            return
        instrument_keys_to_subscribe = [self.main_instrument_key, self.option_key]
        self.streamer.subscribe(instrument_keys_to_subscribe,"full")
        logging.info(f"Subscribing to {self.option_key}")
        self.option_price=self.data_collector.get_option_price(self.option_key)
        if self.option_price is None:
            logging.warning(f"Could not get option price for {option_type}")
            return
        current_atr = None
        if not self.candle_df[SL_ATR_TIMEFRAME].empty and 'atr' in self.candle_df[SL_ATR_TIMEFRAME].columns:
            current_atr = self.candle_df[SL_ATR_TIMEFRAME]['atr'].iloc[-1]
        if current_atr is None or pd.isna(current_atr):
            logging.warning("ATR Unavailable Skipping Entry")
            return
        trigger_price=calculations.calculate_trigger_price(
            current_atr,
            self.option_price
        )
        if trigger_price is None:
            logging.error("Trigger Price Calculation Failed")
            return
        self.trigger_price = math.floor(trigger_price)
        quantity = calculations.calculate_quantity(self.lot_size,self.option_price,self.available_margin,self.trigger_price)
        if quantity <= 0:
            logging.warning("Insufficient margin for trade")
            return
        self.exit_price = math.floor(self.option_price + (self.option_price - self.trigger_price) * R_TO_R_RATIO)
        self.position_active=True
        self.latest_entry_time = datetime.now(pytz.timezone('Asia/Kolkata'))
        # Record the trade
        trade=Trade(self.option_key,self.option_type,self.latest_entry_time,self.option_price,quantity,self.trigger_price,self.exit_price)
        self.transcriber.record_entry(trade)
        logging.info(f"{option_type} Trade: Price={self.option_price}, Qty={quantity}, "
              f"Trigger={self.trigger_price}, Target={self.exit_price}")
        if DRY_RUN:
            logging.info(f"[DRY RUN] Would place {option_type} order: Qty={quantity}, Trigger={self.trigger_price}, Target={self.exit_price}")
        else:
            self.place_order(quantity)
        Alerts.trade_entered()

    def place_order(self,quantity):
        api_instance = upstox_client.OrderApiV3(upstox_client.ApiClient(CONFIGURATION))
        body = upstox_client.PlaceOrderV3Request(quantity=quantity, product="I", validity="DAY", 
            price=0, tag="order", instrument_token=self.option_key, 
            order_type="SL-M", transaction_type="BUY", disclosed_quantity=0, 
            trigger_price=self.trigger_price, is_amo=False, slice=True)
        try:
            api_response = api_instance.place_order(body)
            logging.info(api_response)
        except ApiException as e:
            Alerts.error()
            logging.error(f"Exception While Placing Order :{e}")

    def exit_position(self):
        api_instance = upstox_client.OrderApi(upstox_client.ApiClient(CONFIGURATION))
        try:
            api_response = api_instance.exit_positions()
            logging.info(api_response)
        except ApiException as e:
            Alerts.error()
            logging.error(f"Exception When Exiting Position :{e}")

    def _cleanup_after_exit(self):
        self.streamer.unsubscribe([self.option_key])
        self.streamer.subscribe([self.main_instrument_key], "full")
        self.last_exit_time = datetime.now(pytz.timezone('Asia/Kolkata'))
        self.position_active = False
        self.option_key = self.option_price = self.option_type = None
        self.trigger_price = self.exit_price = None
        self.index_price=None
        if hasattr(self, 'latest_entry_time'):
            del self.latest_entry_time
        Alerts.trade_exited()
