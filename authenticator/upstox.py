from dotenv import load_dotenv,set_key
import upstox_client
from upstox_client.rest import ApiException
from configutarions import trading_config
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
    
    def __init__(self):
        self.check_env_file()
        load_dotenv()
        self.api_key=os.getenv('api_key')
        self.api_secret=os.getenv('api_secret')
        self.redirect_url=os.getenv('redirect_url')
        self.state=os.getenv('state')
        self.url=f"https://api.upstox.com/v2/login/authorization/dialog?response_type=code&client_id={self.api_key}&redirect_uri={self.redirect_url}&state={self.state}"
        self.access_token=os.getenv('access_token')
        self.configuration = upstox_client.Configuration()
        if self.access_token:
            self.configuration.access_token=self.access_token

    def check_env_file(self):
        if not os.path.exists(self.ENV_PATH):
            logging.warning("API details not found.")
            for key in ["api_key", "api_secret", "redirect_url", "state"]:
                set_key(self.ENV_PATH, key, input(f"Enter {key.replace('_',' ').title()}: "))
            set_key(self.ENV_PATH, "access_token", "")
            logging.info("API details saved")

    def get_access_token(self):
        if self.check_token_validity():
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
            self.update_access_token()
            logging.info("Access Token Updated")
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

    def update_access_token(self):
        set_key(self.ENV_PATH, "access_token", self.access_token)
        load_dotenv(self.ENV_PATH, override=True)
        self.access_token = os.getenv("access_token")
        self.configuration.access_token = self.access_token