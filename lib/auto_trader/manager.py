from lib.clients.rds_manager import get_stocks
from lib.clients.alpaca_manager import get_historical_market_prices, get_current_market_prices, Steps, TimeRange
from lib.auto_trader.history_v1 import assess_histories

def orchestrator():
    # Pull all stocks that are being looked at
    stocks = get_stocks().data
    stock_codes = [stock["code"] for stock in stocks]
    # Pull history from all stocks
    short_term = get_historical_market_prices(stock_codes, Steps.HOUR, TimeRange.WEEK)
    long_term = get_historical_market_prices(stock_codes, Steps.DAY, TimeRange.MONTH)
    current = get_current_market_prices(stock_codes)
    # Run histories through logic to determine if buy or sell
    assessments = assess_histories(long_term, short_term, current, stock_codes)
    # buy or sell quantity based on static figure (eventually dynamic figure)

    # Update RDS according to new data (transactions, stocks, and account)

    # Complete job
    return assessments
