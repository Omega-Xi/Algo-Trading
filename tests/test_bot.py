from core.Bot import Bot
from utilities.terminator import Terminator
from utilities.wake_lock import Wake_Lock
import threading

if __name__=="__main__":
    with Wake_Lock():
        bot=Bot()
        terminator=Terminator(bot)
        threading.Thread(target=terminator.listen_for_kill, daemon=True).start()
        bot.launch()