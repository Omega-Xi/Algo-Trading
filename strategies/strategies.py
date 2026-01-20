import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(filename)s:%(lineno)d | %(funcName)s() | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def check_macd_rsi_signal(bot,indicator_results:dict):
    if bot.position_active: 
        logging.info("Position Active Skipping Signal Check") 
        return 
    if not bot.can_enter_trade(): 
        logging.info("Bot in Cooldown Skipping Signal Check") 
        return 
    if bot.index_price is None: 
        logging.warning("Index price not available, Skipping MACD RSI signal check.") 
        return 
    df_5=indicator_results.get("5")
    df_15=indicator_results.get("15")
    if len(df_15) < 26: 
        logging.warning("Not enough data for MACD signal check") 
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
        print(f"Bullish MACD crossover + RSI={rsi_curr:.2f} → Entering CE trade Index Price:{bot.index_price}")
        bot.option_type="CE"
        bot.enter_trade("CE")

    # Bearish
    elif macd_prev > signal_prev and macd_curr < signal_curr and macd_curr < 0:
        # if rsi_curr > self.config.rsi_threshold_low and rsi_curr < 60 and adx_curr > self.config.adx_threshold and adx_curr > adx_prev:
        print(f"Bearish MACD crossover + RSI={rsi_curr:.2f} → Entering PE trade Index Price:{bot.index_price}")
        bot.option_type="PE"
        bot.enter_trade("PE")
