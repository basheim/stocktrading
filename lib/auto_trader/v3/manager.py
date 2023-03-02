from lib.auto_trader.v3.history import write_complete_history, get_current_history_slopes
from lib.clients.rds_manager import get_stocks, update_account
from lib.auto_trader.v3.data_model import find_model
from lib.clients.alpaca_manager import get_account_info, get_current_market_prices, get_historical_market_prices, Steps
from lib.auto_trader.generic.action import buy, sell
from flask import current_app
from datetime import datetime
from lib.objects.history_assessment import HistoryAssessment
from lib.auto_trader.generic.helpers import generate_base_files, delete_all_files
from lib.auto_trader.generic.helpers import decrement_stock_days
from lib.auto_trader.v3.history import StockData, negative_month_day_slope_days, negative_week_hour_slope_days, negative_day_minute_slope_days
from lib.objects.redis_wrapper import RedisData


class MLStockModels(RedisData):

    def __init__(self):
        super().__init__()

    def redis_key(self):
        return "ML_MODELS"

    def initialize(self):
        self.data = {}
        stocks = get_stocks()
        generate_base_files(StockData.get_headers())
        for stock in stocks:
            current_app.logger.info(stock.code)
            write_complete_history(stock.code)
            model = find_model("./.tmp/.tmp_data/.single/raw_data.csv")
            if model:
                self.data[stock.code] = model
        current_app.logger.info("Overall")
        model = find_model("./.tmp/.tmp_data/raw_data.csv")
        if model:
            for stock in stocks:
                if stock.code not in self.data:
                    self.data[stock.code] = model
        delete_all_files()


class StockMonitor(RedisData):

    def __init__(self):
        super().__init__()

    def redis_key(self):
        return "STOCK_MONITORS"

    def initialize(self):
        self.data = {}
        stocks = get_stocks()
        for stock in stocks:
            self.data[stock.code] = True


class StockOpeningPrice(RedisData):

    def __init__(self):
        super().__init__()

    def redis_key(self):
        return "STOCK_OPENING_PRICE"

    def initialize(self):
        current_app.logger.info("---------start assign opening prices----------")
        # Pull all stocks that are being looked at
        stocks = get_stocks()
        stock_codes = [stock.code for stock in stocks]
        # Pull history from all stocks
        current = datetime.now()
        current_data = get_current_market_prices(stock_codes)
        current_app.logger.info(f"Pulling prices at {str(current)}")
        for stock in stocks:
            self.data[stock.code] = current_data[stock.code].ask_price
            current_app.logger.info(f"{stock.code} opening price = {str(current_data[stock.code].ask_price)}")
        current_app.logger.info("---------end assign opening prices----------")


class StockManager:

    def __init__(self):
        self.models = MLStockModels()
        self.monitors = StockMonitor()
        self.opening_prices = StockOpeningPrice()

    def get_opening_price(self, code: str):
        return self.opening_prices.data[code] if code in self.opening_prices.data else None

    def get_monitor(self, code: str):
        return self.monitors.data[code] if code in self.monitors.data else None

    def get_model(self, code: str):
        return self.models.data[code] if code in self.models.data else None

    def __repr__(self):
        return str(
            {
                "models": self.models,
                "monitors": self.monitors,
                "opening_prices": self.opening_prices
            }
        )

    def orchestrator(self):
        current_app.logger.info("---------start assessment review----------")
        # Pull all stocks that are being looked at
        stocks = get_stocks()
        stock_codes = [stock.code for stock in stocks]
        # Pull history from all stocks
        current = datetime.today()
        current_data = get_current_market_prices(stock_codes)
        day_start = decrement_stock_days(current, negative_month_day_slope_days)
        hour_start = decrement_stock_days(current, negative_week_hour_slope_days)
        minute_start = decrement_stock_days(current, negative_day_minute_slope_days)
        day_data = get_historical_market_prices(codes=stock_codes, step=Steps.DAY, start_time=day_start)
        hour_data = get_historical_market_prices(codes=stock_codes, step=Steps.HOUR, start_time=hour_start)
        minute_data = get_historical_market_prices(codes=stock_codes, step=Steps.MINUTE, start_time=minute_start)
        assessments = []
        hold_assessments = []
        for stock in stocks:
            model = self.get_model(stock.code)
            if model:
                stock_data = get_current_history_slopes(stock.code, day_data[stock.code], hour_data[stock.code],
                                                        minute_data[stock.code])
                prediction = model.predict([stock_data.get_as_num_row()])[0]
                assessments.append(HistoryAssessment.build_limited(current_data[stock.code], stock, prediction))
            else:
                hold_assessments.append(HistoryAssessment.build_only_stock_data(current_data[stock.code], stock))

        buy_assessments = []
        current_app.logger.info(f"Assessment count = {len(assessments)}")
        current_app.logger.info(f"Hold Assessment count = {len(hold_assessments)}")
        current_app.logger.info("---------end assessment review----------")
        current_app.logger.info("---------start model monitoring----------")
        self.monitors.load()
        for assessment in assessments:
            if assessment.current.ask_price > 0:
                current_app.logger.info(str(assessment))
                if assessment.buy:
                    self.monitors.data[assessment.code] = False
                    buy_assessments.append(assessment)
        self.monitors.store()
        current_app.logger.info("---------end model monitoring----------")
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

    def monitor(self):
        current_app.logger.info("---------start assessment monitor----------")
        # Pull all stocks that are being looked at
        stocks = get_stocks()
        stock_codes = [stock.code for stock in stocks]
        # Pull history from all stocks
        current_data = get_current_market_prices(stock_codes)
        assessments = []
        for stock in stocks:
            should_monitor = self.get_monitor(stock.code)
            if should_monitor:
                assessment = HistoryAssessment.build_only_stock_data(current_data[stock.code], stock)
                assessment.sell = self.get_opening_price(stock.code) >= current_data[stock.code].ask_price or (assessment.owned_price * 1.01) > current_data[stock.code].ask_price
                assessments.append(assessment)
        current_app.logger.info(f"Assessment count = {len(assessments)}")
        for assessment in assessments:
            if assessment.current.ask_price > 0:
                current_app.logger.info(str(assessment))
                if assessment.sell and assessment.owned > 0:
                    sell(assessment)
        current_app.logger.info("---------start account update----------")
        update_account(float(get_account_info().equity))
        current_app.logger.info("---------end account update----------")
        current_app.logger.info("---------end assessment monitor----------")