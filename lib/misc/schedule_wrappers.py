from flask import current_app
from pandas_market_calendars import get_calendar, date_range
from datetime import datetime, timedelta
from pytz import timezone


def with_function(app, func, passed_args=tuple()):
    with app.app_context():
        current_app.logger.info(f"Background function: ${func.__name__}")
        func(*passed_args)


def stock_wrapper(app, func, passed_args=tuple()):
    d1 = datetime.today() - timedelta(days=1)
    d2 = datetime.today() + timedelta(days=1)
    nyse = get_calendar('NYSE')
    open_date_range = nyse.schedule(start_date=d1, end_date=d2)
    dates = date_range(open_date_range, frequency='1D')
    now = datetime.now(tz=timezone('UTC'))
    for date in dates:
        converted_date = datetime.fromisoformat(str(date))
        if converted_date.day == now.day and now < converted_date:
            with_function(app, func, passed_args)
            break
