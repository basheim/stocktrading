import json
from enum import Enum
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.data import StockHistoricalDataClient
from alpaca.data.requests import StockLatestQuoteRequest, StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from lib.clients.secrets_manager import Secret, get_secret
from datetime import datetime, timedelta


"""
Test Code
"""
secret_json = json.loads(get_secret(Secret.ALPACA)["SecretString"])
API_KEY = secret_json["test_account_id"]
SECRET_KEY = secret_json["test_account_secret_id"]
INITIAL_ACCOUNT_ID = "testInitial"
CURRENT_ACCOUNT_ID = "testCurrent"
trading_client = TradingClient(API_KEY, SECRET_KEY, paper=True)

"""
Real Code
secret_json = json.loads(get_secret(Secret.ALPACA)["SecretString"])
API_KEY = secret_json["account_id"]
SECRET_KEY = secret_json["account_secret_id"]
INITIAL_ACCOUNT_ID = "initial"
CURRENT_ACCOUNT_ID = "current"
trading_client = TradingClient(API_KEY, SECRET_KEY, paper=False)
"""

market_client = StockHistoricalDataClient(API_KEY, SECRET_KEY)


class Steps(Enum):
    HOUR = 1
    DAY = 2


class TimeRange(Enum):
    DAY = 1
    WEEK = 2
    MONTH = 3


def get_historical_market_price(code: str, step: Steps, time_range: TimeRange) -> []:
    days = 0
    configured_step = TimeFrame.Day

    match step:
        case Steps.HOUR: configured_step = TimeFrame.Hour
        case Steps.DAY: configured_step = TimeFrame.Day

    match time_range:
        case TimeRange.DAY: days = 1
        case TimeRange.WEEK: days = 7
        case TimeRange.MONTH: days = 31

    start_time = datetime.today() - timedelta(days)

    return market_client.get_stock_bars(
        StockBarsRequest(
            symbol_or_symbols=code,
            timeframe=configured_step,
            start=start_time
        )
    )[code]


def get_current_market_price(code: str) -> {}:
    return market_client.get_stock_latest_quote(
        StockLatestQuoteRequest(
            symbol_or_symbols=code
        )
    )[code]


def get_account_info() -> {}:
    print(str(trading_client.get_account()))
    return trading_client.get_account()


def execute_buy(code: str, quantity: float) -> {}:
    request = MarketOrderRequest(
        symbol=code,
        qty=quantity,
        side=OrderSide.BUY,
        time_in_force=TimeInForce.GTC
    )
    return trading_client.submit_order(request)


def execute_sell(code: str, quantity: float) -> {}:
    request = MarketOrderRequest(
        symbol=code,
        qty=quantity,
        side=OrderSide.SELL,
        time_in_force=TimeInForce.GTC
    )
    return trading_client.submit_order(request)


def get_positions() -> []:
    return trading_client.get_all_positions()