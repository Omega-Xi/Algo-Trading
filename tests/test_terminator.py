from utilities.terminator import Terminator
import logging
from datetime import datetime
import time
import threading

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(filename)s:%(lineno)d | %(funcName)s() | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

class Mock_Streamer:
    def __init__(self):
        self.is_connected=True
    
    def connect(self):
        logging.info("Streamer Connected")
        while self.is_connected:
            print(datetime.now().strftime("%H:%M:%S"), end="\r", flush=True)
            time.sleep(1)

    def disconnect(self):
        self.is_connected=False
        logging.warning("Streamer Disconnected")

class Mock_Bot:
    def __init__(self):
        self.kill_switch=False
        self.streamer = Mock_Streamer()

    def run(self):
        self.streamer.connect()

if __name__=="__main__":
    bot=Mock_Bot()
    terminator=Terminator(bot)
    threading.Thread(target=terminator.listen_for_kill, daemon=True).start()
    bot.run()
