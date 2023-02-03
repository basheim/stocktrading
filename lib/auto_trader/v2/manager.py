from lib.auto_trader.v2.history import write_complete_history
from lib.clients.rds_manager import get_stocks
from lib.auto_trader.v2.data_model import read_model

def orchestrator():
    stocks = get_stocks()
    for stock in stocks:
        print(stock.code)
        write_complete_history(stock.stock_id)
        read_model()
