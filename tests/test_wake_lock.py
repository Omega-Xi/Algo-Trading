from utilities.wake_lock import Wake_Lock
import time
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(filename)s:%(lineno)d | %(funcName)s() | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

class Mock_Bot:
    @staticmethod
    def start():
        logging.info("Bot Started")
        time.sleep(5)
        logging.info("Bot Stopped")

if __name__=="__main__":
    bot=Mock_Bot()
    with Wake_Lock():
        bot.start()

    