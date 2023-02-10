from lib.auto_trader.v2.history import write_complete_history, generate_base_files, get_current_history_slopes, decrement_stock_days, decrement_stock_hours, negative_hour_range, negative_minute_range, delete_all_files
from lib.clients.rds_manager import get_stocks, update_account
from lib.auto_trader.v2.data_model import find_model
from lib.clients.alpaca_manager import get_account_info, get_current_market_prices, get_historical_market_prices, Steps
from lib.auto_trader.v1.action import buy, sell
from flask import current_app
from datetime import datetime
from lib.objects.history_assessment import HistoryAssessment


class MLStockModels:

    def __init__(self):
        self.models = {}

    def build_models(self):
        self.models = {}
        stocks = get_stocks()
        generate_base_files()
        for stock in stocks:
            current_app.logger.info(stock.code)
            write_complete_history(stock.code)
            model = find_model("./.tmp_data/.single/raw_data.csv")
            if model:
                self.models[stock.code] = model
        current_app.logger.info("Overall")
        model = find_model("./.tmp_data/raw_data.csv")
        if model:
            for stock in stocks:
                if stock.code not in self.models:
                    self.models[stock.code] = model
        delete_all_files()

    def get_model(self, code: str):
        return self.models[code] if code in self.models else None

    def __repr__(self):
        return str(self.models)


def orchestrator(ml_model):
    current_app.logger.info("---------start assessment review----------")
    # Pull all stocks that are being looked at
    stocks = get_stocks()
    stock_codes = [stock.code for stock in stocks]
    # Pull history from all stocks
    current = datetime.today()
    current_data = get_current_market_prices(stock_codes)
    hour_start = decrement_stock_days(current, negative_hour_range)
    minute_day_start = decrement_stock_days(current, negative_minute_range)
    minute_hour_start = decrement_stock_hours(current, negative_minute_range)
    hour_data = get_historical_market_prices(codes=stock_codes, step=Steps.HOUR, start_time=hour_start)
    minute_day_data = get_historical_market_prices(codes=stock_codes, step=Steps.MINUTE, start_time=minute_day_start)
    minute_hour_data = get_historical_market_prices(codes=stock_codes, step=Steps.MINUTE, start_time=minute_hour_start)
    assessments = []
    hold_assessments = []
    for stock in stocks:
        model = ml_model.get_model(stock.code)
        if model:
            stock_data = get_current_history_slopes(stock.code, hour_data[stock.code], minute_day_data[stock.code], minute_hour_data[stock.code])
            prediction = model.predict([stock_data.get_as_num_row()])[0]
            assessments.append(HistoryAssessment.build_limited(current_data[stock.code], stock, prediction))
        else:
            hold_assessments.append(HistoryAssessment.build_only_stock_data(current_data[stock.code], stock))

    buy_assessments = []
    current_app.logger.info(f"Assessment count = {len(assessments)}")
    current_app.logger.info(f"Hold Assessment count = {len(hold_assessments)}")
    current_app.logger.info("---------end assessment review----------")
    current_app.logger.info("---------start sells----------")
    for assessment in assessments:
        if assessment.current.ask_price > 0:
            current_app.logger.info(str(assessment))
            if assessment.buy and assessment.owned == 0:
                buy_assessments.append(assessment)
            if assessment.sell and assessment.owned > 0:
                sell(assessment)
    for assessment in hold_assessments:
        if assessment.current.ask_price > 0:
            current_app.logger.info(str(assessment))
            if assessment.owned > 0 and assessment.current.ask_price < (assessment.owned_price * 1.005):
                sell(assessment)
    current_app.logger.info("---------end sells----------")
    current_app.logger.info("---------start buys----------")
    buying_power = float(get_account_info().buying_power)
    account = float(buying_power - (buying_power * 0.1)) // len(buy_assessments) if len(buy_assessments) > 0 else 0
    current_app.logger.info(f"account: {account}")
    current_app.logger.info(f"buy_assessments: {len(buy_assessments)}")
    if account > 1:
        for assessment in buy_assessments:
            buy(assessment, account)
    else:
        current_app.logger.info(f"buy can not be executed. Account too limited. Account = {account}")
    current_app.logger.info("---------end buys----------")
    current_app.logger.info("---------start account update----------")
    update_account(float(get_account_info().equity))
    current_app.logger.info("---------end account update----------")
    return assessments
