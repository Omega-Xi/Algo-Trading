import winsound

class Alerts:
    def websocket_connected(self):
        winsound.Beep(2000,200)

    def websocket_error(self):
        winsound.Beep(400,200)
        winsound.Beep(400,200)
        winsound.Beep(400,200)
        winsound.Beep(400,3000)

    def websocket_disconnected(self):
        winsound.Beep(1200,1000)

    def trade_entered(self):
        winsound.Beep(900,200)

    def trade_exited(self):
        winsound.Beep(700,200)