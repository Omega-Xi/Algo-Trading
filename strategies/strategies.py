import logging
from configurations.strategy_config import *

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(filename)s:%(lineno)d | %(funcName)s() | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)


def pre_check_validation(bot):
    if bot.position_active: 
        print("Position Active Skipping Signal Check",end="\r") 
        return False
    elif not bot.can_enter_trade():
        print("Bot in Cooldown Skipping Signal Check",end="\r") 
        return False
    elif bot.index_price is None: 
        logging.warning("Index price not available, Skipping MACD RSI signal check.") 
        return False
    else:
        return True

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

        print(f"MACD:{macd_curr:.2f} | SIGNAL:{signal_curr:.2f} | RSI:{rsi_curr:.2f}",end='\r')
        # Bullish
        if macd_prev < signal_prev and macd_curr > signal_curr and macd_curr > 0 and rsi_curr < RSI_TRESHOLD_HIGH:
            logging.info(f"Bullish MACD crossover + RSI={rsi_curr:.2f} → Entering CE trade Index Price:{bot.index_price}")
            bot.option_type="CE"
            bot.enter_trade("CE")

        # Bearish
        elif macd_prev > signal_prev and macd_curr < signal_curr and macd_curr < 0 and rsi_curr > RSI_TRESHOLD_LOW:
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

        if macd_prev < signal_prev and macd_curr > signal_curr and adx_curr > ADX_TRESHOLD and adx_curr > adx_prev:
            logging.info("Bullish MACD+ADX → Enter CE")
            bot.option_type = "CE"
            bot.enter_trade("CE")

        elif macd_prev > signal_prev and macd_curr < signal_curr and adx_curr > ADX_TRESHOLD and adx_curr > adx_prev:
            logging.info("Bearish MACD+ADX → Enter PE")
            bot.option_type = "PE"
            bot.enter_trade("PE")
