from utilities.alerts import Alerts
import logging
import time

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(filename)s:%(lineno)d | %(funcName)s() | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

class Mock_Bot:
    def __init__(self,delay=1):
        self.delay=delay

    def connected(self):
        logging.info("Web Socket Connected")
        Alerts.websocket_connected()
        time.sleep(self.delay)
    
    def disconnected(self):
        logging.info("Web Socket Disconnected")
        Alerts.websocket_disconnected()
        time.sleep(self.delay)

    def error(self):
        logging.critical("Web Socket Error")
        Alerts.websocket_error()
        time.sleep(self.delay)
    
    def enter_trade(self):
        logging.info("Trade Entered")
        Alerts.trade_entered()
        time.sleep(self.delay)

    def exit_trade(self):
        logging.info("Trade Exited")
        Alerts.trade_exited()
        time.sleep(self.delay)

    def run(self):
        self.connected()
        self.enter_trade()
        self.exit_trade()
        self.error()
        self.disconnected()

if __name__=="__main__":
    bot=Mock_Bot()
    bot.run()