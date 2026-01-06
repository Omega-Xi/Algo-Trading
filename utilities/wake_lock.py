import ctypes
import logging
import platform

if platform.system() != "Windows":
    logging.warning("Wake Lock is only supported on Windows. Ensure Network connection is enabled during sleep.")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(filename)s:%(lineno)d | %(funcName)s() | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

class Wake_Lock:
    def __init__(self):
        self.ES_CONTINUOUS       = 0x80000000
        self.ES_SYSTEM_REQUIRED  = 0x00000001
        self.ES_DISPLAY_REQUIRED = 0x00000002
        self.active=False

    def __enter__(self):
        self.activate()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.deactivate()
    
    def activate(self):
        if platform.system() != "Windows":
            return

        if not ctypes.windll.kernel32.SetThreadExecutionState(self.ES_CONTINUOUS | self.ES_SYSTEM_REQUIRED | self.ES_DISPLAY_REQUIRED):
            logging.error("Failed To Activate Wake Lock")
        else:
            self.active=True
            logging.info("Wake Lock Activated")

    def deactivate(self):
        if platform.system() != "Windows":
            return
        
        if not ctypes.windll.kernel32.SetThreadExecutionState(self.ES_CONTINUOUS):
            logging.error("Failed To Deactivate Wake Lock")
        else:
            self.active=False
            logging.info("Wake Lock Deactivated")