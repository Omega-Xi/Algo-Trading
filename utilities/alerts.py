import winsound

class Alerts:
    @staticmethod
    def websocket_connected():
        winsound.PlaySound("./resources/Websocket Connected.wav", winsound.SND_FILENAME)

    @staticmethod
    def websocket_error():
        winsound.Beep(400,200)
        winsound.Beep(400,200)
        winsound.Beep(400,200)
        winsound.Beep(400,3000)

    @staticmethod
    def websocket_disconnected():
        winsound.PlaySound("./resources/Websocket Disconnected.wav", winsound.SND_FILENAME)

    @staticmethod
    def trade_entered():
        winsound.PlaySound("./resources/Trade Entered.wav", winsound.SND_FILENAME)

    @staticmethod
    def trade_exited():
        winsound.PlaySound("./resources/Trade Exited.wav", winsound.SND_FILENAME)

    @staticmethod
    def error():
        winsound.Beep(1000,1000)