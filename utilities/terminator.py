import keyboard
import sys
import logging

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
        keyboard.on_press_key("q",self.kill_bot)

    def kill_bot(self,event=None):
        self.bot.kill_switch = True
        if hasattr(self.bot, "streamer"):
            self.bot.streamer.disconnect()

    def emergency_kill(self,event=None):
        self.bot.kill_switch=True
        if hasattr(self.bot, "streamer"):
            self.bot.streamer.disconnect()
        logging.critical("Emergency stop. Bot Terminated>>>")
        sys.exit(1)