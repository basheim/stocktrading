import subprocess
import uuid
from datetime import datetime, timedelta, date
from lib.clients.rds_manager import get_stock
from alpaca.data.models import Bar
from lib.clients.alpaca_manager import get_historical_market_price, Steps
from lib.auto_trader.v2.equations.predictions import get_slope_in_hours, get_slope_in_minutes


class StockData:
    row_id: str
    stock_id: str
    hour_minute_slope: float
    day_minute_slope: float
    week_hour_slope: float
    profit: float
    hours_since: int

    def __init__(self, stock_id: str):
        self.stock_id = stock_id
        self.row_id = str(uuid.uuid4())
        self.hour_minute_slope = 0
        self.day_minute_slope = 0
        self.week_hour_slope = 0
        self.profit = 0
        self.hours_since = 0

    def __repr__(self):
        return str({
            "row_id": self.row_id,
            "stock_id": self.stock_id,
            "hour_minute_slope": self.hour_minute_slope,
            "day_minute_slope": self.day_minute_slope,
            "week_hour_slope": self.week_hour_slope
        })


def __generate_files():
    subprocess.run("rm -rf ./.tmp_data || true".split())
    subprocess.run("mkdir ./.tmp_data".split())
    subprocess.run("touch ./.tmp_data/raw_data.csv".split())


def __generate_points(bar: Bar):
    temp = []
    temp.append([bar.high, bar.timestamp])
    temp.append([bar.low, bar.timestamp])
    return temp


def __format_data(stock_id: str, dates: [date], hour_data: {date, (Bar)}, minute_data: {date, (Bar)}) -> [StockData]:
    complete_data = []
    hour_history = []
    minute_day_history = []
    for i in range(7):
        temp = hour_data[dates[i]]
        for bar in temp:
            hour_history += __generate_points(bar)
    for bar in minute_data[dates[6]]:
        minute_day_history += __generate_points(bar)
    current = dates[7]
    for i in range(1, len(hour_data[current])):
        index = i * 2
        new_hour_history = []
        new_minute_history = []
        for j in range(i):
            new_hour_history += __generate_points(hour_data[current][j])
        # Need to split the minutes into a hour -> minute map
        for k in range(i * 60):
            new_minute_history += __generate_points(minute_data[current][k])
        temp_hour_history = hour_history[index:] + new_hour_history
        temp_minute_day_history = minute_day_history[60 * index:] + new_minute_history
        temp_minute_hour_history = new_minute_history[-120:]
        hour_slope = get_slope_in_hours(temp_hour_history, ["PRICE", "TIMESTAMP"])
        minute_day_slope = get_slope_in_minutes(temp_minute_day_history, ["PRICE", "TIMESTAMP"])
        minute_hour_slope = get_slope_in_minutes(temp_minute_hour_history, ["PRICE", "TIMESTAMP"])
        stock_data = StockData(stock_id)
        stock_data.week_hour_slope = hour_slope
        stock_data.day_minute_slope = minute_day_slope
        stock_data.hour_minute_slope = minute_hour_slope
        complete_data.append(stock_data)
    return complete_data


def __write_data(csv_data: [StockData]):
    print(str(csv_data))


def __decrement_stock_days(d: datetime, days: int):
    for _ in range(days):
        while not __is_stock_day(d):
            d -= timedelta(days=1)
        d -= timedelta(days=1)
    return d


def __increment_stock_days(d: datetime, days: int):
    for _ in range(days):
        while not __is_stock_day(d):
            d += timedelta(days=1)
        d += timedelta(days=1)
    return d


def __is_stock_day(d: datetime):
    return d.weekday() != 5 and d.weekday() != 6


def __format_map(data: [Bar]) -> {date, (Bar)}:
    temp = {}
    for x in data:
        d = x.timestamp.date()
        if d not in temp:
            temp[d] = []
        temp[d].append(x)
    return temp


def __get_dates(data: [Bar]) -> [date]:
    temp = []
    for x in data:
        d = x.timestamp.date()
        if len(temp) == 0 or temp[-1] != d:
            temp.append(d)
    return temp


def write_complete_history(stock_id: str) -> None:
    __generate_files()
    stock = get_stock(stock_id)
    start = __decrement_stock_days(datetime.today().replace(hour=0, minute=0, second=0, microsecond=0), 6)
    current = start
    end = __decrement_stock_days(datetime.today().replace(hour=0, minute=0, second=0, microsecond=0), 1)
    step = 21
    negative_hour_range = 7
    positive_hour_range = 3
    negative_minute_range = 1
    positive_minute_range = 0
    csv_data = []
    while __increment_stock_days(current, positive_hour_range) < end:
        hour_start = __decrement_stock_days(current, negative_hour_range)
        minute_start = __decrement_stock_days(current, negative_minute_range)
        temp_end = __increment_stock_days(current, step + positive_hour_range)
        while temp_end >= end:
            temp_end = __decrement_stock_days(temp_end, 1)
        hour_end = temp_end
        minute_end = __increment_stock_days(__decrement_stock_days(temp_end, positive_hour_range), positive_minute_range)
        hour_data = get_historical_market_price(code=stock.code, step=Steps.HOUR, start_time=hour_start, end_time=hour_end)
        minute_data = get_historical_market_price(code=stock.code, step=Steps.MINUTE, start_time=minute_start, end_time=minute_end)
        hour_data.sort(key=lambda x: x.timestamp)
        minute_data.sort(key=lambda x: x.timestamp)
        hour_dates = __get_dates(hour_data)
        hour_map = __format_map(hour_data)
        minute_map = __format_map(minute_data)
        for i in range(len(hour_dates)):
            csv_data += __format_data(stock_id, hour_dates[i:i + negative_hour_range + positive_hour_range], hour_map, minute_map)
        current = datetime.combine(hour_dates[-2], datetime.min.time())
    __write_data(csv_data)






