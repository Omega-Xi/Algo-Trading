import logging
from configurations.strategy_config import *

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(filename)s:%(lineno)d | %(funcName)s() | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def pre_check_validation(bot):
    if bot.position_active: 
        if bot.option_type  == "CE":
            print(f"[Active Trade] CE | Stop Loss: {bot.trigger_price} | Current Price: {bot.option_price} | Target: {bot.exit_price}  ",end="\r") 
        else:
            print(f"[Active Trade] PE | Stop Loss: {bot.trigger_price} | Current Price: {bot.option_price} | Target: {bot.exit_price}  ",end="\r") 
        return False
    elif not bot.can_enter_trade():
        if bot.market_closed():
            logging.info("Market is closed. Bot will resume when market opens.")
            bot.stop()
        print("Bot in Sleep Mode",end="\r") 
        return False
    elif bot.futures_price is None: 
        logging.warning("Futures price not available, Skipping signal check.") 
        return False
    else:
        return True

def macd_ema_strategy(bot,indicator_results:dict):
    if pre_check_validation(bot):
        df_1=indicator_results.get("1")
        df_5=indicator_results.get("5")
        df_15=indicator_results.get("15")
        if len(df_5) < 200:
            logging.warning("Not enough data for MACD EMA signal check") 
            return 
        price_curr = df_1["close"].iloc[-1]
        macd_prev, macd_curr = df_5["macd"].iloc[-2], df_5["macd"].iloc[-1] 
        signal_prev, signal_curr = df_5["signal"].iloc[-2], df_5["signal"].iloc[-1] 
        ema200_curr = df_5["ema200"].iloc[-1]
        adx_curr=df_15["adx"].iloc[-1]
        er_curr=df_15["efficiency_ratio"].iloc[-1]
        timestamp_curr = df_1.index[-1].strftime('%H:%M')

        print(f"[{timestamp_curr}]| MACD:{macd_curr:.2f} | SIGNAL:{signal_curr:.2f} | EMA200:{ema200_curr:.2f} | PRICE:{price_curr:.2f} | ADX:{adx_curr:.2f} | ER:{er_curr:.2f} ",end='\r')
        # Bullish
        if macd_prev < signal_prev and macd_curr > signal_curr and price_curr > ema200_curr and adx_curr > STRATEGY_CONFIG["ADX_TRESHOLD"] and er_curr > STRATEGY_CONFIG["ER_TRESHOLD"]:
            logging.info(f"Bullish MACD crossover + Price above EMA200 → Entering CE trade Index Price:{bot.index_price}")
            bot.option_type="CE"
            bot.enter_trade("CE")

        # Bearish
        elif macd_prev > signal_prev and macd_curr < signal_curr and price_curr < ema200_curr and adx_curr > STRATEGY_CONFIG["ADX_TRESHOLD"] and er_curr > STRATEGY_CONFIG["ER_TRESHOLD"]:
            logging.info(f"Bearish MACD crossover + Price below EMA200 → Entering PE trade Index Price:{bot.index_price}")
            bot.option_type="PE"
            bot.enter_trade("PE")

def macd_rsi_strategy(bot,indicator_results:dict):
    if pre_check_validation(bot):
        df_1=indicator_results.get("1")
        df_15=indicator_results.get("15")
        if len(df_15) < 26: 
            logging.warning("Not enough data for MACD RSI signal check") 
            return 
        macd_prev, macd_curr = df_1["macd"].iloc[-2], df_1["macd"].iloc[-1] 
        signal_prev, signal_curr = df_1["signal"].iloc[-2], df_1["signal"].iloc[-1] 
        rsi_curr = df_15["rsi"].iloc[-1]
        adx_prev, adx_curr = df_15["adx"].iloc[-2], df_15["adx"].iloc[-1]
        timestamp_curr = df_1.index[-1].strftime('%H:%M')


        macd_bullish = macd_prev < signal_prev and macd_curr > signal_curr and macd_curr < 0
        macd_bearish = macd_prev > signal_prev and macd_curr < signal_curr and macd_curr > 0
        rsi_bullish = STRATEGY_CONFIG["RSI_TRESHOLD_MID"] < rsi_curr < STRATEGY_CONFIG["RSI_TRESHOLD_HIGH"]
        rsi_bearish = STRATEGY_CONFIG["RSI_TRESHOLD_MID"] > rsi_curr > STRATEGY_CONFIG["RSI_TRESHOLD_LOW"]
        market_strong = adx_curr > STRATEGY_CONFIG["ADX_TRESHOLD"]

        print(f"[{timestamp_curr}]| MACD:{macd_curr:.2f} | SIGNAL:{signal_curr:.2f} | RSI:{rsi_curr:.2f} | ADX:{adx_curr:.2f} ",end='\r')
        # Bullish
        if not market_strong:
            return
        if macd_bullish and rsi_bullish:
            logging.info(f"Bullish MACD crossover + RSI={rsi_curr:.2f} → Entering CE trade Index Price:{bot.index_price}")
            bot.option_type="CE"
            bot.enter_trade("CE")

        # Bearish
        elif macd_bearish and rsi_bearish:
            logging.info(f"Bearish MACD crossover + RSI={rsi_curr:.2f} → Entering PE trade Index Price:{bot.index_price}")
            bot.option_type="PE"
            bot.enter_trade("PE")

def macd_adx_strategy(bot,indicator_results:dict):
    if pre_check_validation(bot):
        df_1 = indicator_results.get("1")
        df_15 = indicator_results.get("15")
        if len(df_15) < 26: 
            logging.warning("Not enough data for MACD ADX signal check") 
            return 
        macd_prev, macd_curr = df_1["macd"].iloc[-2], df_1["macd"].iloc[-1]
        signal_prev, signal_curr = df_1["signal"].iloc[-2], df_1["signal"].iloc[-1]
        adx_prev, adx_curr = df_15["adx"].iloc[-2], df_15["adx"].iloc[-1]
        timestamp_curr = df_1.index[-1].strftime('%H:%M')

        print(f"[{timestamp_curr}]| MACD:{macd_curr:.2f} | SIGNAL:{signal_curr:.2f} | ADX:{adx_curr:.2f} ",end='\r')

        if macd_prev < signal_prev and macd_curr > signal_curr and adx_curr > STRATEGY_CONFIG["ADX_TRESHOLD"] and adx_curr > adx_prev:
            logging.info("Bullish MACD + ADX → Enter CE")
            bot.option_type = "CE"
            bot.enter_trade("CE")

        elif macd_prev > signal_prev and macd_curr < signal_curr and adx_curr > STRATEGY_CONFIG["ADX_TRESHOLD"] and adx_curr > adx_prev:
            logging.info("Bearish MACD + ADX → Enter PE")
            bot.option_type = "PE"
            bot.enter_trade("PE")

def vwap_rsi_strategy(bot,indicator_results:dict):
    if pre_check_validation(bot):
        df=indicator_results.get("3")
        if df is None:
            logging.warning("3-minute indicator data not available for VWAP RSI strategy")
            return
        if len(df) < 15: 
            logging.warning("Not enough data for VWAP RSI signal check") 
            return 
        close_curr = df["close"].iloc[-1]
        close_prev = df["close"].iloc[-2]
        close_last = df["close"].iloc[-3]
        vwap_curr = df["vwap"].iloc[-1]
        vwap_prev = df["vwap"].iloc[-2]
        vwap_last = df["vwap"].iloc[-3]
        rsi_curr = df["rsi"].iloc[-1]
        rsi_prev = df["rsi"].iloc[-2]
        timestamp_curr = df.index[-1].strftime('%H:%M')

        print(f"[{timestamp_curr}] Price: {close_curr:.2f} | VWAP: {vwap_curr:.2f} | RSI: {rsi_curr:.2f}  ", end="\r")

        vwap_crossover_up_curr = (close_prev < vwap_prev and close_curr > vwap_curr * (1 + STRATEGY_CONFIG["VWAP_CLOSE_TOLERANCE"]))
        vwap_crossover_up_prev = (close_last < vwap_last and close_prev > vwap_prev * (1 + STRATEGY_CONFIG["VWAP_CLOSE_TOLERANCE"]))
        rsi_borderline_up_prev = 40 < rsi_prev < STRATEGY_CONFIG["RSI_TRESHOLD_MID"]
        rsi_strong_up = (STRATEGY_CONFIG["RSI_TRESHOLD_MID"] < rsi_curr < STRATEGY_CONFIG["RSI_TRESHOLD_HIGH"])
        vwap_crossover_down_curr = (close_prev > vwap_prev and close_curr < vwap_curr * (1 - STRATEGY_CONFIG["VWAP_CLOSE_TOLERANCE"]))
        vwap_crossover_down_prev = (close_last > vwap_last and close_prev < vwap_prev * (1 - STRATEGY_CONFIG["VWAP_CLOSE_TOLERANCE"]))
        rsi_borderline_down_prev = 60 > rsi_prev > STRATEGY_CONFIG["RSI_TRESHOLD_MID"]
        rsi_strong_down = (STRATEGY_CONFIG["RSI_TRESHOLD_LOW"] < rsi_curr < STRATEGY_CONFIG["RSI_TRESHOLD_MID"])

        if vwap_crossover_up_curr and rsi_strong_up:
            logging.info(f"[STAGE 1] CE Immediate Entry VWAP Crossover + RSI Match | Price:{close_curr:.2f} > VWAP:{vwap_curr:.2f} | RSI:{rsi_curr:.2f} | Index:{bot.index_price}")
            bot.option_type = "CE"
            bot.enter_trade("CE")

        elif vwap_crossover_up_prev and rsi_strong_up and rsi_borderline_up_prev:
            logging.info(f"[STAGE 2] CE Delayed Entry VWAP Crossover Prev + RSI Match | Price:{close_curr:.2f} > VWAP:{vwap_curr:.2f} | RSI:{rsi_curr:.2f} | Index:{bot.index_price}")
            bot.option_type = "CE"
            bot.enter_trade("CE")

        elif vwap_crossover_down_curr and rsi_strong_down:
            logging.info(f"[STAGE 1] PE Immediate Entry VWAP Crossover + RSI Match | Price:{close_curr:.2f} < VWAP:{vwap_curr:.2f} | RSI:{rsi_curr:.2f} | Index:{bot.index_price}")
            bot.option_type = "PE"
            bot.enter_trade("PE")

        elif vwap_crossover_down_prev and rsi_strong_down and rsi_borderline_down_prev:
            logging.info(f"[STAGE 2] PE Delayed Entry VWAP Crossover Prev + RSI Match | Price:{close_curr:.2f} < VWAP:{vwap_curr:.2f} | RSI:{rsi_curr:.2f} | Index:{bot.index_price}")
            bot.option_type = "PE"
            bot.enter_trade("PE")

def bollinger_rsi_mean_reversion(bot, indicator_results: dict):
    if pre_check_validation(bot):
        df = indicator_results.get("5")
        if df is None or len(df) < 30:
            logging.warning("Not enough data for Bollinger RSI strategy")
            return

        close_curr = df["close"].iloc[-1]
        upper_band = df["bb_upper"].iloc[-1]
        lower_band = df["bb_lower"].iloc[-1]
        rsi_curr = df["rsi"].iloc[-1]
        timestamp_curr = df.index[-1].strftime('%H:%M')

        print(f"[{timestamp_curr}] Price:{close_curr:.2f} | BB_Upper:{upper_band:.2f} | BB_Lower:{lower_band:.2f} | RSI:{rsi_curr:.2f}", end="\r")

        # Overbought → Expect pullback
        if close_curr > upper_band and rsi_curr > STRATEGY_CONFIG["RSI_TRESHOLD_HIGH"]:
            logging.info(f"Overbought: Price above BB Upper + RSI={rsi_curr:.2f} → Enter PE | Index:{bot.index_price}")
            bot.option_type = "PE"
            bot.enter_trade("PE")

        # Oversold → Expect bounce
        elif close_curr < lower_band and rsi_curr < STRATEGY_CONFIG["RSI_TRESHOLD_LOW"]:
            logging.info(f"Oversold: Price below BB Lower + RSI={rsi_curr:.2f} → Enter CE | Index:{bot.index_price}")
            bot.option_type = "CE"
            bot.enter_trade("CE")

def di_adx_strategy(bot, indicator_results: dict):
    if pre_check_validation(bot):
        df_15 = indicator_results.get("15")  # use 15-min candles for stronger signals
        if df_15 is None or len(df_15) < 26:
            logging.warning("Not enough data for DI/ADX strategy")
            return

        plus_di_prev, plus_di_curr = df_15["plus_di"].iloc[-2], df_15["plus_di"].iloc[-1]
        minus_di_prev, minus_di_curr = df_15["minus_di"].iloc[-2], df_15["minus_di"].iloc[-1]
        adx_prev, adx_curr = df_15["adx"].iloc[-2], df_15["adx"].iloc[-1]
        timestamp_curr = df_15.index[-1].strftime('%H:%M')

        print(f"[{timestamp_curr}] +DI:{plus_di_curr:.2f} | -DI:{minus_di_curr:.2f} | ADX:{adx_curr:.2f}", end="\r")

        market_strong = adx_curr > STRATEGY_CONFIG["ADX_TRESHOLD"] and adx_curr > adx_prev

        bullish_condition = plus_di_curr > minus_di_curr and plus_di_curr > plus_di_prev
        bearish_condition = minus_di_curr > plus_di_curr and minus_di_curr > minus_di_prev


        # Bullish condition: +DI > -DI and ADX rising
        if bullish_condition and market_strong:
            logging.info(f"DI+ > DI- with ADX rising → Enter CE | Index:{bot.index_price}")
            bot.option_type = "CE"
            bot.enter_trade("CE")

        # Bearish condition: -DI > +DI and ADX rising
        elif bearish_condition and market_strong:
            logging.info(f"DI- > DI+ with ADX rising → Enter PE | Index:{bot.index_price}")
            bot.option_type = "PE"
            bot.enter_trade("PE")

def golden_strategy(bot, indicator_results: dict):
    if pre_check_validation(bot):
        df = indicator_results.get("15")
        if df is None or len(df) < 30:
            logging.warning("Not enough data for Golden Strategy")
            return

        # Extract indicators
        macd_curr, signal_curr = df["macd"].iloc[-1], df["signal"].iloc[-1]
        rsi_curr = df["rsi"].iloc[-1]
        plus_di_curr, minus_di_curr = df["plus_di"].iloc[-1], df["minus_di"].iloc[-1]
        adx_prev, adx_curr = df["adx"].iloc[-2], df["adx"].iloc[-1]
        atr_curr = df["atr"].iloc[-1]
        atr_ma = df["atr"].rolling(window=20).mean().iloc[-1]
        close_curr = df["close"].iloc[-1]
        upper_band, lower_band = df["bb_upper"].iloc[-1], df["bb_lower"].iloc[-1]
        vwap_curr = df["vwap"].iloc[-1]
        timestamp_curr = df.index[-1].strftime('%H:%M')

        print(f"[{timestamp_curr}] Price:{close_curr:.2f} | MACD:{macd_curr:.2f} | RSI:{rsi_curr:.2f} | ADX:{adx_curr:.2f} | ATR:{atr_curr:.2f}", end="\r")

        # Market regime filters
        market_trending = adx_curr > STRATEGY_CONFIG["ADX_TRESHOLD"] and adx_curr > adx_prev
        market_breakout = atr_curr > atr_ma * 1.5

        # Trending Market
        if market_trending:
            if plus_di_curr > minus_di_curr and macd_curr > signal_curr and rsi_curr > 60 and close_curr > vwap_curr:
                logging.info("Golden Strategy → Bullish Trend Entry (CE)")
                bot.option_type = "CE"
                bot.enter_trade("CE")
            elif minus_di_curr > plus_di_curr and macd_curr < signal_curr and rsi_curr < 40 and close_curr < vwap_curr:
                logging.info("Golden Strategy → Bearish Trend Entry (PE)")
                bot.option_type = "PE"
                bot.enter_trade("PE")

        # Range-Bound Market
        elif not market_trending:
            if close_curr < lower_band and rsi_curr < STRATEGY_CONFIG["RSI_TRESHOLD_LOW"]:
                logging.info("Golden Strategy → Oversold Mean Reversion (CE)")
                bot.option_type = "CE"
                bot.enter_trade("CE")
            elif close_curr > upper_band and rsi_curr > STRATEGY_CONFIG["RSI_TRESHOLD_HIGH"]:
                logging.info("Golden Strategy → Overbought Mean Reversion (PE)")
                bot.option_type = "PE"
                bot.enter_trade("PE")

        # Volatility Breakout
        if market_breakout and market_trending:
            if close_curr > upper_band:
                logging.info("Golden Strategy → Volatility Breakout Bullish (CE)")
                bot.option_type = "CE"
                bot.enter_trade("CE")
            elif close_curr < lower_band:
                logging.info("Golden Strategy → Volatility Breakout Bearish (PE)")
                bot.option_type = "PE"
                bot.enter_trade("PE")
