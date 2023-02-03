import json
from enum import Enum
from alpaca.trading.client import TradingClient, TradeAccount
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.data import StockHistoricalDataClient, Quote
from alpaca.data.requests import StockLatestQuoteRequest, StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from alpaca.data.models import Bar
from lib.clients.secrets_manager import Secret, get_secret
from datetime import datetime, timedelta


"""
Test Code
"""
secret_json = json.loads(get_secret(Secret.ALPACA)["SecretString"])
API_KEY = secret_json["test_account_id"]
SECRET_KEY = secret_json["test_account_secret_id"]
trading_client = TradingClient(API_KEY, SECRET_KEY, paper=True)

"""
Real Code
secret_json = json.loads(get_secret(Secret.ALPACA)["SecretString"])
API_KEY = secret_json["account_id"]
SECRET_KEY = secret_json["account_secret_id"]
trading_client = TradingClient(API_KEY, SECRET_KEY, paper=False)
"""

market_client = StockHistoricalDataClient(API_KEY, SECRET_KEY)


class Steps(Enum):
    HOUR = 1
    DAY = 2
    MINUTE = 3


class TimeRange(Enum):
    DAY = 1
    WEEK = 2
    MONTH = 3
    YEAR = 4


def get_historical_market_prices(codes: [str], step: Steps, time_range: TimeRange = None, start_time: datetime = None, end_time: datetime = None) -> {str: [Bar]} or [Bar]:

    configured_step = TimeFrame.Day
    match step:
        case Steps.HOUR:
            configured_step = TimeFrame.Hour
        case Steps.DAY:
            configured_step = TimeFrame.Day
        case Steps.MINUTE:
            configured_step = TimeFrame.Minute

    if time_range:
        days = 0

        match time_range:
            case TimeRange.DAY: days = 1
            case TimeRange.WEEK: days = 7
            case TimeRange.MONTH: days = 31
            case TimeRange.YEAR: days = 365

        start_time = datetime.today() - timedelta(days)
        end_time = None

    return market_client.get_stock_bars(
        StockBarsRequest(
            symbol_or_symbols=codes,
            timeframe=configured_step,
            start=start_time,
            end=end_time
        )
    ).data


def get_historical_market_price(code: str, step: Steps, time_range: TimeRange = None, start_time: datetime = None, end_time: datetime = None) -> [Bar]:
    data = get_historical_market_prices([code], step, time_range, start_time, end_time)
    return data[code]


def get_current_market_prices(codes: [str]) -> {str, Quote} or Quote:
    return market_client.get_stock_latest_quote(
        StockLatestQuoteRequest(
            symbol_or_symbols=codes
        )
    )


def get_current_market_price(code: str) -> Quote:
    return get_current_market_prices([code])[code]


def get_account_info() -> TradeAccount:
    return trading_client.get_account()


def get_order(order_id: str):
    return trading_client.get_order_by_id(order_id)


def cancel_order(order_id: str):
    return trading_client.cancel_order_by_id(order_id)


def execute_buy(code: str, quantity: float) -> {}:
    request = MarketOrderRequest(
        symbol=code,
        qty=quantity,
        side=OrderSide.BUY,
        time_in_force=TimeInForce.DAY
    )
    return trading_client.submit_order(request)


def execute_sell(code: str, quantity: float) -> {}:
    request = MarketOrderRequest(
        symbol=code,
        qty=quantity,
        side=OrderSide.SELL,
        time_in_force=TimeInForce.DAY
    )
    return trading_client.submit_order(request)


def get_positions() -> []:
    return trading_client.get_all_positions()
