import winsound

class Alerts:
    @staticmethod
    def websocket_connected():
        winsound.Beep(2000,200)

    @staticmethod
    def websocket_error():
        winsound.Beep(400,200)
        winsound.Beep(400,200)
        winsound.Beep(400,200)
        winsound.Beep(400,3000)

    @staticmethod
    def websocket_disconnected():
        winsound.Beep(1200,1000)

    @staticmethod
    def trade_entered():
        winsound.Beep(900,200)

    @staticmethod
    def trade_exited():
        winsound.Beep(700,200)

    @staticmethod
    def error():
        winsound.Beep(1000,1000)