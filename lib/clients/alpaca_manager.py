import json
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from lib.clients.secrets_manager import Secret, get_secret

"""
Test Code
"""
secret_json = json.loads(get_secret(Secret.ALPACA)["SecretString"])
API_KEY = secret_json["test_account_id"]
SECRET_KEY = secret_json["test_account_secret_id"]
INITIAL_ACCOUNT_ID = "testInitial"
CURRENT_ACCOUNT_ID = "testCurrent"

"""
Real Code
secret_json = json.loads(get_secret(Secret.ALPACA)["SecretString"])
API_KEY = secret_json["account_id"]
SECRET_KEY = secret_json["account_secret_id"]
INITIAL_ACCOUNT_ID = "initial"
CURRENT_ACCOUNT_ID = "current"
"""

trading_client = TradingClient(API_KEY, SECRET_KEY, paper=True)


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