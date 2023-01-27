from lib.clients.rds_manager import get_stocks, update_account
from lib.clients.alpaca_manager import get_historical_market_prices, get_current_market_prices, Steps, TimeRange
from lib.auto_trader.v1.history import create_histories
from lib.auto_trader.v1.decision import should_buy, should_sell
from lib.clients.alpaca_manager import get_account_info
from lib.auto_trader.v1.action import buy, sell

def orchestrator():
    # Pull all stocks that are being looked at
    stocks = get_stocks()
    stock_codes = [stock.code for stock in stocks]
    # Pull history from all stocks
    short_term = get_historical_market_prices(stock_codes, Steps.HOUR, TimeRange.WEEK)
    long_term = get_historical_market_prices(stock_codes, Steps.DAY, TimeRange.MONTH)
    current = get_current_market_prices(stock_codes)
    # Create histories
    assessments = create_histories(long_term, short_term, current, stocks)
    # Determine if buy or sell
    buy_assessments = 0
    for assessment in assessments.values():
        should_sell(assessment)
        should_buy(assessment)
        if assessment.buy:
            buy_assessments += 1
        if assessment.sell:
            sell(assessment)
    account = float(get_account_info().buying_power) // buy_assessments if buy_assessments > 0 else 0
    for assessment in assessments.values():
        if assessment.buy:
            buy(assessment, account)
    update_account(float(get_account_info().equity))
    # Complete job
    return assessments
