from models.trade_record import Trade
from models.transcriber import Transcriber
from services.reporting import generate_performance_report
from services.exporter import export_trades_to_excel
from datetime import datetime
import pytz

if __name__=="__main__":
    transcriber=Transcriber(initial_margin=100000)

    trade1=Trade(len(transcriber.trades),"NIFTY","CE", datetime.now(pytz.timezone('Asia/Kolkata')),100,30,95,110)
    transcriber.record_entry(trade1)
    transcriber.record_exit(95,"Stop Loss Hit", datetime.now(pytz.timezone('Asia/Kolkata')))

    trade2=Trade(len(transcriber.trades),"NIFTY","CE", datetime.now(pytz.timezone('Asia/Kolkata')),100,40,95,110)
    transcriber.record_entry(trade2)
    transcriber.record_exit(110,"Target Hit", datetime.now(pytz.timezone('Asia/Kolkata')))

    generate_performance_report(transcriber)

    export_trades_to_excel(transcriber.trades)