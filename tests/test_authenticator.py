from authenticator.upstox_authenticator import Authenticator

class Mock_Bot:
    def __init__(self):
        self.authenticator=Authenticator()

    def run(self):
        self.access_token=self.authenticator.get_access_token()

if __name__=="__main__":
    bot=Mock_Bot()
    bot.run()