import upstox_client
from upstox_client import MarketDataStreamerV3
from upstox_client.rest import ApiException
import webbrowser
import pandas as pd
import math
from datetime import datetime,timezone,date,timedelta
import os
import ctypes
from dotenv import load_dotenv,set_key
import threading
import keyboard
import winsound
import pytz
import numpy as np
import ta

class Terminator:
    def listen_for_kill(self,bot):
        keyboard.wait("q")
        print("Kill switch activated. Disconnecting stream...")
        bot.kill_switch = True
        if hasattr(bot, "streamer"):
            bot.streamer.disconnect()
        bot.transcriber.generate_performance_report()

    def emergency_kill(self,bot):
        keyboard.wait("esc")
        bot.kill_switch=True
        if hasattr(bot, "streamer"):
            bot.streamer.disconnect()
        print("Emergency stop.Bot Terminated>>>")
        os._exit(1)

class Wake_Lock:
    def __init__(self):
        self.ES_CONTINUOUS       = 0x80000000
        self.ES_SYSTEM_REQUIRED  = 0x00000001
        self.ES_DISPLAY_REQUIRED = 0x00000002
    
    def activate(self):
        ctypes.windll.kernel32.SetThreadExecutionState(self.ES_CONTINUOUS | self.ES_SYSTEM_REQUIRED | self.ES_DISPLAY_REQUIRED)
        print("Wake Lock Activated")

    def deactivate(self):
        ctypes.windll.kernel32.SetThreadExecutionState(self.ES_CONTINUOUS)
        print("Wake Lock Deactivated")

class Alerts:
    def websocket_connected(self):
        winsound.Beep(2000,200)

    def websocket_error(self):
        winsound.Beep(400,200)
        winsound.Beep(400,200)
        winsound.Beep(400,200)
        winsound.Beep(400,3000)

    def websocket_disconnected(self):
        winsound.Beep(1200,2000)

    def trade_entered(self):
        winsound.Beep(900,200)

    def trade_exited(self):
        winsound.Beep(700,200)

class Transcriber:
    def __init__(self,initial_margin):
        self.trades=[]
        self.position=None
        self.initial_balance=initial_margin
        self.current_balance=self.initial_balance
        self.tax=0

    def record_entry(self, name, option_type, entry_price, quantity, trigger_price, target_price, timestamp):
        trade = {
            'trade_id': len(self.trades) + 1,
            'instrument': name,
            'type': option_type,
            'entry_time': timestamp,
            'entry_price': entry_price,
            'quantity': quantity,
            'trigger_price': trigger_price,
            'target_price': target_price,
            'exit_time': None,
            'exit_price': None,
            'pnl': 0,
            'status': 'ACTIVE'
        }
        self.trades.append(trade)
        self.position = option_type
        print(f"Trade recorded: {option_type} at {entry_price} , Time: {timestamp}")

    def record_exit(self, exit_price, exit_reason, timestamp):
        if not self.trades or self.position is None:
            print("No active trade to exit")
            return

        active_trade = None
        for trade in reversed(self.trades):
            if trade['status'] == 'ACTIVE':
                active_trade = trade
                break

        if active_trade:
            active_trade['exit_time'] = timestamp
            active_trade['exit_price'] = exit_price
            active_trade['status'] = 'CLOSED'
            active_trade['exit_reason'] = exit_reason

            # Charges
            charges = self.calculate_charges(
                active_trade['entry_price'],
                exit_price,
                active_trade['quantity'],
                product_type="intraday"
            )

            # Gross & Net P&L
            gross_pnl = (exit_price - active_trade['entry_price']) * active_trade['quantity']
            net_pnl = gross_pnl - charges["total_charges"]

            active_trade['gross_pnl'] = gross_pnl
            active_trade['net_pnl'] = net_pnl
            active_trade['charges'] = charges
            active_trade['pnl'] = net_pnl   # ✅ ensures reports use net P&L

            # Update balance
            self.current_balance += net_pnl
            print(f"Trade exited: {active_trade['type']} at {exit_price}, "
                f"Gross P&L: {gross_pnl:.2f}, Net P&L: {net_pnl:.2f}, Time: {timestamp}")

            self.position = None

    def calculate_charges(self, entry_price, exit_price, quantity, product_type="intraday", brokerage_fee=30):
        turnover = (entry_price + exit_price) * quantity
        buy_value = entry_price * quantity
        sell_value = exit_price * quantity

        # Brokerage (flat per trade, adjust if you want entry+exit)
        brokerage = brokerage_fee*2

        # STT
        if product_type == "delivery":
            stt = 0.001 * (buy_value + sell_value)
        elif product_type == "intraday":
            stt = 0.00025 * sell_value
        elif product_type == "futures":
            stt = 0.000125 * sell_value
        elif product_type == "options":
            stt = 0.000625 * sell_value
        else:
            stt = 0

        # Exchange Transaction Charges
        txn_charges = 0.0000325 * turnover

        # SEBI Fees
        sebi_fees = 0.000001 * turnover

        # Stamp Duty
        if product_type == "delivery":
            stamp_duty = 0.00015 * buy_value
        elif product_type == "intraday":
            stamp_duty = 0.00003 * buy_value
        elif product_type == "futures":
            stamp_duty = 0.00002 * buy_value
        elif product_type == "options":
            stamp_duty = 0.00003 * buy_value
        else:
            stamp_duty = 0

        # GST
        gst = 0.18 * (brokerage + txn_charges)

        total_charges = brokerage + stt + txn_charges + sebi_fees + stamp_duty + gst

        return {
            "brokerage": brokerage,
            "stt": stt,
            "txn_charges": txn_charges,
            "sebi_fees": sebi_fees,
            "stamp_duty": stamp_duty,
            "gst": gst,
            "total_charges": total_charges
        }

    def generate_performance_report(self):
        if not self.trades:
            print("No trades to generate report")
            return
            
        # Calculate performance metrics
        closed_trades = [trade for trade in self.trades if trade['status'] == 'CLOSED']
        active_trades = [trade for trade in self.trades if trade['status'] == 'ACTIVE']
        
        print("\n" + "="*60)
        print("FINAL TRADING PERFORMANCE REPORT")
        print("="*60)
        
        # Show active trades first
        if active_trades:
            print(f"\nACTIVE TRADES: {len(active_trades)}")
            print("-" * 40)
            for trade in active_trades:
                print(f"Trade {trade['trade_id']}: {trade['type']} | Entry: {trade['entry_price']} | "
                      f"Qty: {trade['quantity']} | Target: {trade['target_price']}")
        
        # Show closed trades performance
        if closed_trades:
            total_pnl = sum(trade['pnl'] for trade in closed_trades)
            winning_trades = [trade for trade in closed_trades if trade['pnl'] > 0]
            losing_trades = [trade for trade in closed_trades if trade['pnl'] < 0]
            breakeven_trades = [trade for trade in closed_trades if trade['pnl'] == 0]
            
            win_rate = len(winning_trades) / len(closed_trades) * 100 if closed_trades else 0
            avg_win = sum(trade['pnl'] for trade in winning_trades) / len(winning_trades) if winning_trades else 0
            avg_loss = sum(trade['pnl'] for trade in losing_trades) / len(losing_trades) if losing_trades else 0
            
            profit_factor = abs(sum(trade['pnl'] for trade in winning_trades) / 
                              sum(trade['pnl'] for trade in losing_trades)) if losing_trades else float('inf')
            total_gross = sum(t['gross_pnl'] for t in closed_trades)
            total_net   = sum(t['net_pnl'] for t in closed_trades)
            total_charges = sum(t['charges']['total_charges'] for t in closed_trades)
            
            print(f"\nCLOSED TRADES PERFORMANCE:")
            print("-" * 40)
            print(f"Initial Balance:    ₹{self.initial_balance:,.2f}")
            print(f"Final Balance:      ₹{self.current_balance:,.2f}")
            print(f"Gross P&L:          ₹{total_gross:.2f}")
            print(f"Net P&L:            ₹{total_net:.2f}")
            print(f"Total Charges:      ₹{total_charges:.2f}")
            print(f"Total P&L:          ₹{total_pnl:,.2f}")
            print(f"Return:             {(total_pnl/self.initial_balance)*100:.2f}%")
            print(f"Total Trades:       {len(closed_trades)}")
            print(f"Winning Trades:     {len(winning_trades)}")
            print(f"Losing Trades:      {len(losing_trades)}")
            print(f"Breakeven Trades:   {len(breakeven_trades)}")
            print(f"Win Rate:           {win_rate:.2f}%")
            print(f"Average Win:        ₹{avg_win:,.2f}")
            print(f"Average Loss:       ₹{avg_loss:,.2f}")
            print(f"Profit Factor:      {profit_factor:.2f}")
            
            if winning_trades:
                print(f"Largest Win:        ₹{max(trade['pnl'] for trade in winning_trades):,.2f}")
            if losing_trades:
                print(f"Largest Loss:       ₹{min(trade['pnl'] for trade in losing_trades):,.2f}")
            
            # Show individual trade details
            print(f"\nTRADE DETAILS:")
            print("-" * 80)
            print(f"{'ID':<3} {'Type':<4} {'Entry':<8} {'Exit':<8} {'Qty':<6} {'P&L':<10} {'Reason'}")
            print("-" * 80)
            for trade in closed_trades:
                print(f"{trade['trade_id']:<3} {trade['type']:<4} {trade['entry_price']:<8.2f} "
                      f"{trade['exit_price']:<8.2f} {trade['quantity']:<6} "
                      f"₹{trade['pnl']:<8.2f} {trade.get('exit_reason', 'N/A')}")
        else:
            print("\nNo closed trades to analyze")
        
        print("=" * 60)

    def export_trades_to_excel(self, filename='trade_log.xlsx'):
        if not self.trades:
            print("No trades to export.")
            return

        df = pd.DataFrame(self.trades)
        
        # Optional: reorder columns for better readability
        column_order = [
                        'trade_id','instrument','type','entry_time','entry_price','quantity',
                        'trigger_price','target_price','exit_time','exit_price',
                        'gross_pnl','net_pnl','pnl','status','exit_reason'
                    ]
        df = df[[col for col in column_order if col in df.columns]]

        try:
            df.to_excel(filename, index=False)
            print(f"Trade log successfully exported to '{filename}'")
        except Exception as e:
            print(f"Failed to export trades: {e}")

class Authenticator:
    def __init__(self):
        self.load_environment_variables()
        self.configuration = upstox_client.Configuration()
        self.configuration.access_token=self.access_token

    def load_environment_variables(self):
        load_dotenv()
        self.api_key=os.getenv('api_key')
        self.api_secret=os.getenv('api_secret')
        self.redirect_url=os.getenv('redirect_url')
        self.state=os.getenv('state')
        self.url=f"https://api.upstox.com/v2/login/authorization/dialog?response_type=code&client_id={self.api_key}&redirect_uri={self.redirect_url}&state={self.state}"
        self.access_token=os.getenv('access_token')
        self.valid_token=None
    
    def get_access_token(self):
        self.valid_token=self.check_token_validity()
        if(self.valid_token):
            return self.access_token
        else:
            self.generate_access_token()
            return self.access_token

    def generate_access_token(self):
        webbrowser.open(self.url)
        new_uri=input("Enter Redirect URL:")
        code=self.get_code(new_uri)
        self.fetch_token(code)
        if self.access_token:
            self.update_access_token()
            print(f"Access Token Updated")
            return
        else:
            print("Invalid Code")
            return

    def get_code(self,new_uri):
        try:
            code=new_uri[new_uri.index('code=')+5:new_uri.index('&state')]
            return code
        except:
            print("Invalid URL")
            return

    def fetch_token(self,code):
        api_instance = upstox_client.LoginApi()
        api_version = '2.0'
        grant_type = 'authorization_code'

        try:
            # Get token API
            api_response = api_instance.token(api_version, code=code, client_id=self.api_key, client_secret=self.api_secret,
                                            redirect_uri=self.redirect_url, grant_type=grant_type)
            self.access_token=api_response.access_token
        except ApiException as e:
            self.access_token=None
            print("Access Denied:",e)

    def check_token_validity(self):
        api_version='2.0'
        api_instance = upstox_client.PortfolioApi(upstox_client.ApiClient(self.configuration))

        try:
            api_response = api_instance.get_positions(api_version)
            if(api_response):
                return True
        except ApiException as e:
            print("Token Expired")
            return False

    def update_access_token(self):
        dotenv_path = ".env"
        load_dotenv(dotenv_path)
        set_key(dotenv_path, "access_token", self.access_token)
        load_dotenv(dotenv_path, override=True)
        self.access_token = os.getenv("access_token")
        self.configuration.access_token = self.access_token

class Data_Collector:
    def __init__(self,access_token,dry_run,name,instruments,config):
        self.access_token=access_token
        self.configuration = upstox_client.Configuration()
        self.configuration.access_token = self.access_token
        self.dry_run=dry_run
        self.name=name
        self.instruments=instruments
        self.instrument_key=None
        self.option_key=None
        self.expiry_date=None
        self.option_price=None
        self.available_margin=None
        self.config=config
    
    def get_margin(self):
        print("Fetching Margin Details...")
        if self.dry_run:
            self.available_margin=self.config.dry_run_margin
            print("Dry Run Margin Fetched")
            return self.available_margin
        self.configuration.access_token = self.access_token
        api_version = '2.0'

        api_instance = upstox_client.UserApi(upstox_client.ApiClient(self.configuration))

        try:
            # Get User Fund And Margin
            api_response = api_instance.get_user_fund_margin(api_version)
            self.available_margin=api_response.data['equity'].available_margin
            print("Margin Fetched Successfully")
            return self.available_margin
        except ApiException as e:
            print(f"Exception when fetchin margin details:{e}")
            return

    def get_lot_size(self):
        futures = self.instruments[
            (self.instruments['segment'] == "NSE_FO") &
            (self.instruments['underlying_symbol'] == self.name)
        ]
        futures_sorted = futures.sort_values(by='expiry')
        if not futures_sorted.empty:
            lot_size=int(futures_sorted.iloc[0]['lot_size'])
            print(f"{self.name} Lot Size : {lot_size}")
            return lot_size
        else:
            raise ValueError(f"No Futures Found For Instrument: {self.name}")

    def get_historic_data(self,instrument_key):
        today=date.today()
        previous_day=today-timedelta(days=7)
        str_today=str(today)
        str_previous_day=str(previous_day)

        apiInstance = upstox_client.HistoryV3Api(upstox_client.ApiClient(self.configuration))
        try:
            response_1 = apiInstance.get_historical_candle_data1(instrument_key, self.config.time_unit, "1", str_today, str_previous_day)
            response_5 = apiInstance.get_historical_candle_data1(instrument_key, self.config.time_unit, "5", str_today, str_previous_day)
            response_10 = apiInstance.get_historical_candle_data1(instrument_key, self.config.time_unit, "10", str_today, str_previous_day)
            response_15 = apiInstance.get_historical_candle_data1(instrument_key, self.config.time_unit, "15", str_today, str_previous_day)

            df_1 = self.convert_to_df(response_1)
            df_5 = self.convert_to_df(response_5)
            df_10 = self.convert_to_df(response_10)
            df_15 = self.convert_to_df(response_15)
            
            return df_1, df_5, df_10, df_15
        except Exception as e:
            print("Exception when calling HistoryV3Api->get_historical_candle_data1: %s\n" % e)

    def get_intraday_data(self,instrument_key):
        api_instance = upstox_client.HistoryV3Api(upstox_client.ApiClient(self.configuration))
        try:
            response_1 = api_instance.get_intra_day_candle_data(instrument_key, self.config.time_unit, "1")
            response_5 = api_instance.get_intra_day_candle_data(instrument_key, self.config.time_unit, "5")
            response_10 = api_instance.get_intra_day_candle_data(instrument_key, self.config.time_unit, "10")
            response_15 = api_instance.get_intra_day_candle_data(instrument_key, self.config.time_unit, "15")

            df_1 = self.convert_to_df(response_1)
            df_5 = self.convert_to_df(response_5)
            df_10 = self.convert_to_df(response_10)
            df_15 = self.convert_to_df(response_15)

            return df_1, df_5, df_10, df_15
        except Exception as e:
            print("Exception when calling HistoryV3Api->get_intra_day_candle_data: %s\n" % e)

    def get_instrument_key(self):
        filtered=self.instruments[self.instruments['trading_symbol']==self.name]['instrument_key']
        if filtered.empty:
            print("Instrument Key Not Found")
            return
        self.instrument_key=filtered.squeeze()
        print(f"Instrument Key: {self.instrument_key}")
        return self.instrument_key

    def get_expiry_date(self):
        print("Fetching Nearest Expiry...")
        try:
            instruments=self.instruments[self.instruments['name']==self.name]
            instruments_sorted = instruments.sort_values(by='expiry')
            first_expiry = instruments_sorted['expiry'].dropna().sort_values().iloc[0]
            first_expiry = first_expiry.strftime('%Y-%m-%d')
            self.expiry_date=first_expiry 
            return self.expiry_date
        except Exception as e:
            print(f"Unable To Fetch Expiry : {e}")

    def get_option_key(self,order_type,index_price):
        if index_price is None:
            print("Index price not available for option key calculation")
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
            print(f"Option key not found for {order_type}, {self.name}, {self.expiry_date}, {strike_price}")
            return None
        self.option_key=option_key.squeeze()
        return self.option_key

    def get_option_price(self):
        if self.option_key is None:
            print("Invalid option key")
            return None
        self.configuration.access_token = self.access_token
        api_instance = upstox_client.MarketQuoteV3Api(upstox_client.ApiClient(self.configuration))
        try:
            response = api_instance.get_ltp(instrument_key=self.option_key)
            last_trade_price = response.data[next(iter(response.data))].last_price
            if last_trade_price:
                self.option_price=last_trade_price
                print(self.option_price)
                return self.option_price
            else:
                print("No candle data available.")
                return None
        except ApiException as e:
            print(f"API Exception: {e}")
        except Exception as e:
            print(f"Exception when fetching option price: {e}")
            return None

    def get_quantity(self,lot_size):
        if self.option_price <= 0:
            print("Invalid option price for quantity calculation")
            return 0
        usable_margin=(self.config.margin_percentage)*self.available_margin
        max_lots=usable_margin//(self.option_price*lot_size)
        quantity=int(max_lots)*lot_size
        return max(quantity, 0)  # Ensure non-negative quantity

    def get_trigger_price(self, quantity, current_atr=None, option_price=None, use_atr=True):
        if quantity <= 0:
            return 0
        
        if use_atr and current_atr is not None and option_price is not None:
            # Dynamic stop based on ATR
            atr_stop = current_atr * self.config.atr_multiplier
            trigger_price = option_price - atr_stop
            
            # Ensure minimum stop loss percentage
            min_stop = option_price * (1 - self.config.minimum_sl_percentage/100)
            max_stop = option_price * (1 - self.config.maximum_sl_percentage/100)
            
            trigger_price = max(trigger_price, min_stop)  # Not too tight
            trigger_price = min(trigger_price, max_stop)  # Not too loose
            
        else:
            # Fallback to percentage-based (improved)
            risk_margin = self.config.risk_percentage * self.available_margin
            # Increase risk percentage for wider stops
            adjusted_risk_percentage = max(self.config.risk_percentage, 0.02)  # Minimum 2%
            risk_margin = adjusted_risk_percentage * self.available_margin
            risk_per_unit = risk_margin / quantity
            trigger_price = option_price - risk_per_unit
        
        return round(max(trigger_price, 0.05), 2)  # Ensure positive, minimum 0.05

    def check_position(self):
        api_version='2.0'
        api_instance = upstox_client.PortfolioApi(upstox_client.ApiClient(self.configuration))

        try:
            api_response = api_instance.get_positions(api_version)
            if(api_response.data):
                return True
            else:
                return False
        except ApiException as e:
            print("Exception when calling ChargeApi->get_brokerage: %s\n" % e)

    def convert_to_df(self,response):
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

class Strategies:
    def compute_macd_rsi(self,candle_df):
        df = candle_df.copy()
        df["ema12"] = df["close"].ewm(span=12,adjust=False).mean()
        df["ema26"] = df["close"].ewm(span=26,adjust=False).mean()
        df["macd"] = df["ema12"] - df["ema26"]
        df["signal"] = df["macd"].ewm(span=9,adjust=False).mean()

        # --- RSI Calculation ---
        delta = df["close"].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.ewm(alpha=1/14, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1/14, adjust=False).mean()
        rs = avg_gain / avg_loss.replace(0, np.nan)
        df["rsi"] = 100 - (100 / (1 + rs))

        # --- ATR Calculation (RMA) ---
        df['high_low']   = df['high'] - df['low']
        df['high_close'] = (df['high'] - df['close'].shift()).abs()
        df['low_close']  = (df['low'] - df['close'].shift()).abs()
        df['tr']         = df[['high_low', 'high_close', 'low_close']].max(axis=1)
        df['atr'] = df['tr'].ewm(alpha=1/14, adjust=False).mean()

        # --- Directional Movement ---
        up_move   = df['high'].diff()
        down_move = -df['low'].diff()

        df['plus_dm']  = np.where((up_move > down_move) & (up_move > 0), up_move, 0.0)
        df['minus_dm'] = np.where((down_move > up_move) & (down_move > 0), down_move, 0.0)

        # --- DI using RMA ---
        plus_dm_rma  = df['plus_dm'].ewm(alpha=1/14, adjust=False).mean()
        minus_dm_rma = df['minus_dm'].ewm(alpha=1/14, adjust=False).mean()

        df['plus_di']  = 100 * (plus_dm_rma / df['atr'])
        df['minus_di'] = 100 * (minus_dm_rma / df['atr'])

        # --- DX and ADX (RMA) ---
        df['dx'] = 100 * (abs(df['plus_di'] - df['minus_di']) / (df['plus_di'] + df['minus_di']))
        df['dx'] = df['dx'].fillna(0) 
        df['adx'] = df['dx'].ewm(alpha=1/14, adjust=False).mean()

        return df

class Config:
    def __init__(self):
        self.rsi_threshold_low = 30
        self.rsi_threshold_high = 70
        self.margin_percentage=0.3
        self.risk_percentage=0.01
        self.dry_run_margin=300000
        self.adx_threshold=20
        self.time_interval="15"
        self.time_unit="minutes"
        self.time_period="15min"
         # Parameters for better stop loss
        self.atr_multiplier = 1.5
        self.minimum_sl_percentage = 1.5
        self.maximum_sl_percentage = 3.0
        self.use_atr_stop = True
        self.sl_to_target_ratio = 2 

class Trading_Bot:
    def __init__(self,wake_lock,alert,authenticator):
        self.authenticator=authenticator
        self.access_token=authenticator.access_token
        self.wake_lock=wake_lock
        self.alert=alert
        self.load_instruments()
        self.today=datetime.today().strftime('%y-%m-%d')
        self.available_margin=None
        self.name=None
        self.lot_size=None
        self.main_instrument_key=None
        self.expiry_date=None
        self.dry_run=True
        self.kill_switch=False
        self.configuration = upstox_client.Configuration()
        self.streamer=None
        self.status="OFFLINE"
        self.tick_buffer = []
        self.strategy=Strategies()
        self.candle_df_1 = pd.DataFrame()
        self.candle_df_5 = pd.DataFrame()
        self.candle_df_10 = pd.DataFrame()
        self.candle_df_15 = pd.DataFrame()
        self.historic_df_1 = pd.DataFrame()
        self.historic_df_5 = pd.DataFrame()
        self.historic_df_10 = pd.DataFrame()
        self.historic_df_15 = pd.DataFrame()
        self.intraday_df_1 = pd.DataFrame()
        self.intraday_df_5 = pd.DataFrame()
        self.intraday_df_10 = pd.DataFrame()
        self.intraday_df_15 = pd.DataFrame()
        self.entry_lock=threading.Lock()
        self.exit_lock=threading.Lock()
        self.config=Config()
        self.position_active=False
        self.option_type=None
        self.option_key=None
        self.index_price=None
        self.option_price=None
        self.trigger_price=None
        self.exit_price=None
        self.latest_entry_time=None
        self.last_exit_time = None
        self.entry_cooldown = 30
        self.data_collector=None

    def load_instruments(self):
        self.instruments=pd.read_json("https://assets.upstox.com/market-quote/instruments/exchange/NSE.json.gz")
        self.instruments['expiry']=pd.to_datetime(self.instruments['expiry'],unit='ms',errors='coerce')
        self.instruments['expiry']=self.instruments['expiry'].dt.date
        self.instruments['expiry']=pd.to_datetime(self.instruments['expiry'])

    def can_enter_trade(self):
        
        if self.last_exit_time is None:
            return True
        now_aware = datetime.now(pytz.timezone('Asia/Kolkata'))
        elapsed = (now_aware - self.last_exit_time).total_seconds()
        return elapsed >= self.entry_cooldown

    def launch(self):
        self.name=input("Instrument name:")
        self.access_token=self.authenticator.get_access_token()
        self.data_collector=Data_Collector(self.access_token,self.dry_run,self.name,self.instruments,self.config)
        self.available_margin=self.data_collector.get_margin()
        self.transcriber=Transcriber(self.available_margin)
        self.lot_size=self.data_collector.get_lot_size()
        self.main_instrument_key=self.data_collector.get_instrument_key()
        self.expiry_date=self.data_collector.get_expiry_date()
        self.historic_df_1,self.historic_df_5,self.historic_df_10,self.historic_df_15=self.data_collector.get_historic_data(self.main_instrument_key)
        self.intraday_df_1,self.intraday_df_5,self.intraday_df_10,self.intraday_df_15=self.data_collector.get_intraday_data(self.main_instrument_key)
        self.start_connection()

    def start_connection(self):
        self.configuration.access_token=self.access_token
        self.streamer = MarketDataStreamerV3(
            upstox_client.ApiClient(self.configuration),
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
        print("WebSocket connection opened")
        self.status="ONLINE"
        self.wake_lock.activate()
        self.alert.websocket_connected()

    def on_error(self, error):
        print("Error:", error)
        self.status="ERROR"
        self.alert.websocket_error()

    def on_close(self,*args):
        print("Websocket Closed")
        self.status="OFFLINE"
        self.alert.websocket_disconnected()
        self.wake_lock.deactivate()

    def on_message(self,message):
        if self.kill_switch:
            print("Bot is killed. Ignoring incoming messages.")
            return    
        if "feeds" not in message or not message["feeds"]:
            print("No feed data available")
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

                            if not self.dry_run:
                                self.position_active = self.data_collector.check_position()
                                if not self.position_active:
                                    print(f"Stop loss hit: {ltp} <= {self.trigger_price}, position exited via SL-M.")
                                    self.transcriber.record_exit(ltp, "STOPLOSS_HIT", timestamp)
                                    self._cleanup_after_exit()
                                    self.alert.trade_exited()
                                    return

                            if ltp <= self.trigger_price:
                                print(f"Stop loss hit: {ltp} <= {self.trigger_price}, position exited via SL-M.")
                                self.transcriber.record_exit(ltp, "STOPLOSS_HIT", timestamp)
                                self._cleanup_after_exit()
                                return

                            if ltp >= self.exit_price:
                                print(f"Target reached: {ltp} >= {self.exit_price}, exiting position.")
                                self.transcriber.record_exit(ltp, "TARGET_HIT", timestamp)
                                if not self.dry_run:
                                    self.exit_position()
                                self._cleanup_after_exit()
                                return
                    finally:
                        self.exit_lock.release()
                else:
                    print("exit_lock busy, skipping exit check")
            except KeyError as e:
                print(f"Data access error: {e} - possibly unexpected data structure")
            except Exception as e:
                print(f"Unexpected error: {e}")

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
        self.alert.trade_exited()

    def aggregate_candles(self):
        df = pd.DataFrame(self.tick_buffer)
        if df.empty:
            return
        df.set_index("timestamp", inplace=True)
        df = df.between_time("09:15", "15:30")
        self.candle_df_1=self.convert_to_candles(df,"1min",self.historic_df_1,self.intraday_df_1)
        self.candle_df_5=self.convert_to_candles(df,"5min",self.historic_df_5,self.intraday_df_5)
        self.candle_df_10=self.convert_to_candles(df,"10min",self.historic_df_10,self.intraday_df_10)
        self.candle_df_15=self.convert_to_candles(df,"15min",self.historic_df_15,self.intraday_df_15)
        
        macd_df_1=self.strategy.compute_macd_rsi(self.candle_df_1)
        macd_df_5=self.strategy.compute_macd_rsi(self.candle_df_5)
        macd_df_10=self.strategy.compute_macd_rsi(self.candle_df_10)
        macd_df_15=self.strategy.compute_macd_rsi(self.candle_df_15)
        if self.entry_lock.acquire(blocking=False):
            try:
                self.check_macd_rsi_signal(macd_df_1,macd_df_5,macd_df_10,macd_df_15)
            finally:
                self.entry_lock.release()
        else:
            print("Entry_lock busy, skipping signal check")

    def check_macd_rsi_signal(self, df_1, df_5, df_10, df_15): 
        if self.position_active: 
            print("Position Active Skipping Signal Check",end='\r') 
            return 
        if not self.can_enter_trade(): 
            print("Bot in Cooldown Skipping Signal Check",end='\r') 
            return 
        if self.index_price is None: 
            print("Index price not available yet, skipping MACD signal check.") 
            return 
        if len(df_15) < 26: 
            print("Not enough data for MACD signal check") 
            return 
        macd_prev, macd_curr = df_5["macd"].iloc[-2], df_5["macd"].iloc[-1] 
        signal_prev, signal_curr = df_5["signal"].iloc[-2], df_5["signal"].iloc[-1] 
        rsi_prev, rsi_curr = df_15["rsi"].iloc[-2], df_15["rsi"].iloc[-1]
        adx_prev, adx_curr = df_15["adx"].iloc[-2], df_15["adx"].iloc[-1]
        atr = df_15["atr"].iloc[-1]

        print(f"MACD:{macd_curr:.2f} | SIGNAL:{signal_curr:.2f} | RSI:{rsi_curr:.2f} | ATR:{atr:.2f} | ADX:{adx_curr:.2f}",end='\r')
        # Bullish
        if macd_prev < signal_prev and macd_curr > signal_curr and macd_curr > 0:
            #if rsi_curr < self.config.rsi_threshold_high and rsi_curr > 40 and adx_curr > self.config.adx_threshold and adx_curr > adx_prev:
            print(f"Bullish MACD crossover + RSI={rsi_curr:.2f} → Entering CE trade Index Price:{self.index_price}")
            self.option_type="CE"
            self.enter_trade("CE")

        # Bearish
        elif macd_prev > signal_prev and macd_curr < signal_curr and macd_curr < 0:
            # if rsi_curr > self.config.rsi_threshold_low and rsi_curr < 60 and adx_curr > self.config.adx_threshold and adx_curr > adx_prev:
            print(f"Bearish MACD crossover + RSI={rsi_curr:.2f} → Entering PE trade Index Price:{self.index_price}")
            self.option_type="PE"
            self.enter_trade("PE")

    def enter_trade(self,option_type):
        if self.position_active:
            print("Trade Already taken,Skipping new Entries...")
            return
        self.option_key=self.data_collector.get_option_key(option_type,self.index_price)
        instrument_keys_to_subscribe = [self.main_instrument_key, self.option_key]
        self.streamer.subscribe(instrument_keys_to_subscribe,"full")
        print(f"Subscribing to {self.option_key}")
        if self.option_key is None:
            print(f"Could not find option key for {option_type}")
            return
        self.option_price=self.data_collector.get_option_price()
        if self.option_price is None:
            print(f"Could not get option price for {option_type}")
            return
        quantity = self.data_collector.get_quantity(self.lot_size)
        if quantity <= 0:
            print("Insufficient margin for trade")
            return
        current_atr = None
        if not self.candle_df_15.empty and 'atr' in self.candle_df_15.columns:
            current_atr = self.candle_df_15['atr'].iloc[-1]
        self.trigger_price = math.floor(self.data_collector.get_trigger_price(
            quantity, 
            current_atr=current_atr,
            option_price=self.option_price,
            use_atr=self.config.use_atr_stop
        ))
        self.exit_price = math.floor(self.option_price + (self.option_price - self.trigger_price) * self.config.sl_to_target_ratio)
        self.position_active=True
        self.latest_entry_time = datetime.now(pytz.timezone('Asia/Kolkata'))
        # Record the trade
        self.transcriber.record_entry(self.name,option_type, self.option_price, quantity, self.trigger_price, self.exit_price, datetime.now(pytz.timezone('Asia/Kolkata')))
        print(f"{option_type} Trade: Price={self.option_price}, Qty={quantity}, "
              f"Trigger={self.trigger_price}, Target={self.exit_price}")
        if self.dry_run:
            print(f"[DRY RUN] Would place {option_type} order: Qty={quantity}, Trigger={self.trigger_price}, Target={self.exit_price}")
        else:
            self.place_order(quantity)
        self.alert.trade_entered()
    
    def place_order(self,quantity):
        api_instance = upstox_client.OrderApiV3(upstox_client.ApiClient(self.configuration))
        body = upstox_client.PlaceOrderV3Request(quantity=quantity, product="I", validity="DAY", 
            price=0, tag="order", instrument_token=self.option_key, 
            order_type="SL-M", transaction_type="BUY", disclosed_quantity=0, 
            trigger_price=self.trigger_price, is_amo=False, slice=True)
        try:
            api_response = api_instance.place_order(body)
            print(api_response)
        except ApiException as e:
            print("Exception when calling OrderApiV3->place_order: %s\n" % e)

    def exit_position(self):
        api_instance = upstox_client.OrderApi(upstox_client.ApiClient(self.configuration))
        try:
            api_response = api_instance.exit_positions()
            print(api_response)
        except ApiException as e:
            print("Exception when calling OrderApi->exit all positions: %s\n" % e.body)

    def convert_to_candles(self,df,time_frame,historic_df,intraday_df):
        resampled = df["price"].resample(time_frame).ohlc().dropna()
        frames = [historic_df, intraday_df, resampled]
        frames = [df for df in frames if not df.empty]   # exclude empties
        candle_df = pd.concat(frames) if frames else pd.DataFrame()
        # Remove duplicate index values 
        candle_df = candle_df[~candle_df.index.duplicated(keep='last')]
        return candle_df

class Ui_Bot(Trading_Bot):
    def __init__(self, wake_lock, alert, authenticator):
        super().__init__(wake_lock, alert, authenticator)

class Ui_Authenticator(Authenticator):
    def __init__(self):
        super().__init__()

    def get_new_uri(self):
        webbrowser.open(self.url)

    def generate_access_token(self,new_uri):
        code=self.get_code(new_uri)
        self.fetch_token(code)
        if self.access_token:
            self.update_access_token()
            print(f"Access Token Updated")
            return True
        else:
            print("Invalid Code")
            return False

class Ui_Data_Collector(Data_Collector):
    def __init__(self, access_token, dry_run, name, instruments):
        super().__init__(access_token, dry_run, name, instruments)

    def get_instrument_key(self,name):
        self.name=name
        filtered=self.instruments[self.instruments['trading_symbol']==self.name]['instrument_key']
        if filtered.empty:
            print("Instrument Key Not Found")
            return
        self.instrument_key=filtered.squeeze()
        print(f"Instrument Key: {self.instrument_key}")
        return self.instrument_key

    def get_margin(self,dry_run):
        self.dry_run=dry_run
        print("Fetching Margin Details...")
        if self.dry_run:
            self.available_margin=self.config.dry_run_margin
            print("Dry Run Margin Fetched")
            return self.available_margin
        self.configuration.access_token = self.access_token
        api_version = '2.0'

        api_instance = upstox_client.UserApi(upstox_client.ApiClient(self.configuration))

        try:
            # Get User Fund And Margin
            api_response = api_instance.get_user_fund_margin(api_version)
            self.available_margin=api_response.data['equity'].available_margin
            print("Margin Fetched Successfully")
            return self.available_margin
        except ApiException as e:
            print(f"Exception when fetchin margin details:{e}")
            return

    def get_lot_size(self):
        futures = self.instruments[
            (self.instruments['segment'] == "NSE_FO") &
            (self.instruments['underlying_symbol'] == self.name)
        ]
        futures_sorted = futures.sort_values(by='expiry')
        if not futures_sorted.empty:
            lot_size=int(futures_sorted.iloc[0]['lot_size'])
            print(f"{self.name} Lot Size : {lot_size}")
            return lot_size
        else:
            raise ValueError(f"No Futures Found For Instrument: {self.name}")

    def get_user_details(self):
        api_version = '2.0'
        api_instance = upstox_client.UserApi(upstox_client.ApiClient(self.configuration))
        try:
            # Get User Fund And Margin
            api_response = api_instance.get_profile(api_version)
            self.user_name=api_response.data.user_name
            self.user_id=api_response.data.user_id
            self.user_email=api_response.data.email
            self.user_status=("ACTIVE" if api_response.data.is_active else "INACTIVE")
        except ApiException as e:
            print("Exception when calling UserApi->get_user_fund_margin: %s\n" % e)

class Ui_Terminator(Terminator):
    def listen_for_kill(self, bot):
        print("Kill switch activated....")
        bot.kill_switch = True
        try:
            if hasattr(bot, "streamer"):
                bot.streamer.disconnect()
                print("Disconnecting Stream....")
        except AttributeError:
            print("No stream available for disconnection")

    def emergency_kill(self,bot):
        bot.kill_switch=True
        try:
            if hasattr(bot, "streamer"):
                bot.streamer.disconnect()
                print("Disconnecting Stream....")
        except:
            print("No stream available for disconnection")
        print("Emergency stop Terminating Bot >>>>")
        os._exit(0)

if __name__=="__main__":
    wake_lock=Wake_Lock()
    alert=Alerts()
    authenticator=Authenticator()
    terminator=Terminator()
    bot=Trading_Bot(wake_lock,alert,authenticator)
    threading.Thread(target=terminator.listen_for_kill, args=(bot,), daemon=True).start()
    threading.Thread(target=terminator.emergency_kill, args=(bot,), daemon=True).start()
    bot.launch()