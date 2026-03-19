import keyboard
import sys
import logging
from configurations.trading_config import DRY_RUN

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(filename)s:%(lineno)d | %(funcName)s() | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

class Terminator:
    def __init__(self,bot):
        self.bot=bot
    
    def listen_for_kill(self):
        keyboard.on_press_key("esc",self.emergency_kill)
        keyboard.on_press_key("f12",self.kill_bot)

    def kill_bot(self,event=None):
        self.bot.kill_switch = True
        if not DRY_RUN:
            if self.bot.data_collector.check_position():
                logging.info("Open Position Found. Exiting Trade Before Shutdown")
                self.bot.exit_trade()
        if hasattr(self.bot, "streamer") and self.bot.streamer is not None:
            self.bot.streamer.disconnect()
        logging.info("Bot Stopped Gracefully")

    def emergency_kill(self,event=None):
        self.bot.kill_switch=True
        if hasattr(self.bot, "streamer") and self.bot.streamer is not None:
            self.bot.streamer.disconnect()
        logging.critical("Emergency stop. Bot Terminated>>>")
        sys.exit(1)