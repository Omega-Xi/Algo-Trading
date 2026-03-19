from dotenv import load_dotenv,set_key
import os
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(filename)s:%(lineno)d | %(funcName)s() | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

class Credential_Handler:
    ENV_PATH = ".env"

    def __init__(self):
        if not self.check_env_file():
            logging.warning("Environment file not found. Please provide API credentials.")
        else:
            self.get_credentials_from_env()

    def check_env_file(self):
        return os.path.exists(self.ENV_PATH)
    
    @staticmethod
    def get_credentials_from_env():
        load_dotenv()
        api_key=os.getenv('api_key')
        api_secret=os.getenv('api_secret')
        redirect_url=os.getenv('redirect_url')
        state=os.getenv('state')
        access_token=os.getenv('access_token')
        return api_key,api_secret,redirect_url,state,access_token
    
    @staticmethod
    def save_credentials_to_env(api_key, api_secret, redirect_url, state):
        set_key(Credential_Handler.ENV_PATH, "api_key", api_key)
        set_key(Credential_Handler.ENV_PATH, "api_secret", api_secret)
        set_key(Credential_Handler.ENV_PATH, "redirect_url", redirect_url)
        set_key(Credential_Handler.ENV_PATH, "state", state)
        set_key(Credential_Handler.ENV_PATH, "access_token", "")

    @staticmethod
    def load_access_token_from_env():
        load_dotenv(Credential_Handler.ENV_PATH)
        access_token=os.getenv("access_token")
        return access_token
    
    @staticmethod
    def get_api_credentials_from_console():
        for key in ["api_key", "api_secret", "redirect_url", "state"]:
            set_key(Credential_Handler.ENV_PATH, key, input(f"Enter {key.replace('_',' ').title()}: "))
        set_key(Credential_Handler.ENV_PATH, "access_token", "")
        logging.info("API details saved")

    @staticmethod
    def update_access_token(access_token):
        set_key(Credential_Handler.ENV_PATH, "access_token", access_token)
        load_dotenv(Credential_Handler.ENV_PATH, override=True)
        logging.info("Access Token Updated")
        access_token = os.getenv("access_token")
        return access_token