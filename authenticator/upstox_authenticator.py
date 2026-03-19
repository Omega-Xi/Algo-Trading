from dotenv import load_dotenv,set_key
import upstox_client
from upstox_client.rest import ApiException
from authenticator.credential_handler import Credential_Handler
from configurations import trading_config
import os
import webbrowser
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(filename)s:%(lineno)d | %(funcName)s() | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

class Authenticator:
    GRANT_TYPE = 'authorization_code'
    ENV_PATH = ".env"
    
    def __init__(self,mode="console"):
        if not self.check_env_file():
            logging.warning("Environment file not found. Please provide API credentials.")
            if mode=="console":
                Credential_Handler.get_api_credentials_from_console()    
                self.load_credentials()
        else:
            self.load_credentials()

    def check_env_file(self):
        return os.path.exists(self.ENV_PATH)

    def load_credentials(self):
        self.api_key, self.api_secret, self.redirect_url, self.state, self.access_token = Credential_Handler.get_credentials_from_env()
        self.url=f"https://api.upstox.com/v2/login/authorization/dialog?response_type=code&client_id={self.api_key}&redirect_uri={self.redirect_url}&state={self.state}"
        self.configuration = upstox_client.Configuration()
        if self.access_token:
            self.configuration.access_token=self.access_token
        
    def get_access_token(self):
        if self.check_token_validity():
            logging.info("Access Token Validity Confirmed")
            return self.access_token
        self.generate_access_token()
        return self.access_token

    def generate_access_token(self):
        webbrowser.open(self.url)
        new_uri=input("Enter Redirect URL:")
        code=self.get_code(new_uri)
        if not code:
            logging.error("Invalid Redirect URL")
            return
        self.fetch_token(code)
        if self.access_token:
            self.access_token=Credential_Handler.update_access_token(self.access_token)
            self.configuration.access_token = self.access_token
        else:
            logging.error("Invalid Code")

    def get_code(self,uri):
        try:
            return uri.split("code=")[1].split("&state")[0]
        except Exception:
            return

    def fetch_token(self,code):
        api_instance = upstox_client.LoginApi()
        try:
            # Get token API
            api_response = api_instance.token(trading_config.API_VERSION, code=code, client_id=self.api_key, client_secret=self.api_secret,redirect_uri=self.redirect_url, grant_type=self.GRANT_TYPE)
            self.access_token=api_response.access_token
        except ApiException as e:
            logging.error(f"Access Denied : {e}")
            self.access_token=None

    def check_token_validity(self):
        api_instance = upstox_client.PortfolioApi(upstox_client.ApiClient(self.configuration))
        try:
            return bool(api_instance.get_positions(trading_config.API_VERSION))
        except ApiException as e:
            logging.warning("Token Expired")
            return False