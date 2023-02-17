import uuid
from datetime import datetime, date
from lib.clients.alpaca_manager import get_historical_market_price, Steps
from lib.auto_trader.generic.equations.predictions import get_slope_in_hours, get_slope_in_minutes, get_slope_in_days
from lib.auto_trader.generic.helpers import generate_single_files, generate_points, increment_stock_days, decrement_stock_days, format_day_map, get_dates, write_data


negative_day_minute_slope_days = 1
negative_week_hour_slope_days = 7
negative_month_day_slope_days = 30
positive_day_minute_slope_days = 0
positive_week_hour_slope_days = 0
positive_month_day_slope_days = 2
data_limit = 8


class StockData:
    row_id: str
    stock_code: str
    month_day_slope: float
    day_minute_slope: float
    week_hour_slope: float
    state: str

    def __init__(self, stock_code: str):
        self.stock_code = stock_code
        self.row_id = str(uuid.uuid4())
        self.month_day_slope = 0
        self.day_minute_slope = 0
        self.week_hour_slope = 0
        self.state = "sell"

    @staticmethod
    def build(stock_data):
        temp = StockData(stock_data.stock_id)
        temp.week_hour_slope = stock_data.week_hour_slope
        temp.day_minute_slope = stock_data.day_minute_slope
        temp.month_day_slope = stock_data.month_day_slope
        temp.state = stock_data.state
        return temp

    @staticmethod
    def get_headers():
        return ["month_day_slope", "week_hour_slope", "day_minute_slope", "state"]

    def get_as_num_row(self):
        return [self.month_day_slope, self.week_hour_slope, self.day_minute_slope]

    def get_as_row(self):
        return [str(self.month_day_slope), str(self.week_hour_slope), str(self.day_minute_slope), str(self.state)]

    def __repr__(self):
        return str({
            "row_id": self.row_id,
            "stock_code": self.stock_code,
            "month_day_slope": self.month_day_slope,
            "day_minute_slope": self.day_minute_slope,
            "week_hour_slope": self.week_hour_slope,
            "state": self.state
        })


def __format_data(stock_code: str, dates: [date], month_day_data: any, week_hour_data: any, day_minute_data: any) -> [StockData]:
    complete_data = []
    month_day_history = []
    week_hour_history = []
    day_minute_history = []
    if dates[negative_month_day_slope_days - negative_week_hour_slope_days] not in week_hour_data or dates[negative_month_day_slope_days - negative_day_minute_slope_days] not in day_minute_data:
        return complete_data
    current = dates[negative_month_day_slope_days]
    next_day = dates[negative_month_day_slope_days + 1]
    # Generate histories
    for d in dates:
        if d >= current:
            break
        for bar in month_day_data[d]:
            month_day_history += generate_points(bar)
        if d >= dates[negative_month_day_slope_days - negative_week_hour_slope_days]:
            for bar in week_hour_data[d]:
                week_hour_history += generate_points(bar)
        if d >= dates[negative_month_day_slope_days - negative_day_minute_slope_days]:
            for bar in day_minute_data[d]:
                day_minute_history += generate_points(bar)
    # Generate slopes
    month_day_slope = get_slope_in_days(month_day_history, ["PRICE", "TIMESTAMP"])
    week_hour_slope = get_slope_in_hours(week_hour_history, ["PRICE", "TIMESTAMP"])
    day_minute_slope = get_slope_in_minutes(day_minute_history, ["PRICE", "TIMESTAMP"])
    # Build stock data
    stock_data = StockData(stock_code)
    stock_data.month_day_slope = month_day_slope
    stock_data.week_hour_slope = week_hour_slope
    stock_data.day_minute_slope = day_minute_slope
    current_price = month_day_data[current][0].open
    next_day_price = month_day_data[next_day][0].open
    if next_day_price > current_price:
        stock_data.state = "buy"
    complete_data.append(stock_data)
    return complete_data


def write_complete_history(stock_id: str) -> None:
    generate_single_files(StockData.get_headers())
    __write_complete_history_helper(stock_id, 300, 1, "raw_data.csv")


def __write_complete_history_helper(stock_code: str, start: int, end: int, file: str) -> None:
    start = decrement_stock_days(datetime.today().replace(hour=0, minute=0, second=0, microsecond=0), start)
    current = start
    end = decrement_stock_days(datetime.today().replace(hour=0, minute=0, second=0, microsecond=0), end)
    step = 21

    while increment_stock_days(current, positive_month_day_slope_days) < end:
        csv_data = []
        day_start = decrement_stock_days(current, negative_month_day_slope_days)
        hour_start = decrement_stock_days(current, negative_week_hour_slope_days)
        minute_start = decrement_stock_days(current, negative_day_minute_slope_days)
        temp_end = increment_stock_days(current, step + positive_month_day_slope_days)
        while temp_end >= end:
            temp_end = decrement_stock_days(temp_end, 1)
        day_end = temp_end
        hour_end = increment_stock_days(decrement_stock_days(temp_end, positive_month_day_slope_days), positive_week_hour_slope_days)
        minute_end = increment_stock_days(decrement_stock_days(temp_end, positive_month_day_slope_days), positive_day_minute_slope_days)
        if minute_start >= minute_end or hour_start >= hour_end or day_start >= day_end:
            break
        day_data = get_historical_market_price(code= stock_code, step=Steps.DAY, start_time=day_start, end_time=day_end)
        hour_data = get_historical_market_price(code=stock_code, step=Steps.HOUR, start_time=hour_start, end_time=hour_end)
        minute_data = get_historical_market_price(code=stock_code, step=Steps.MINUTE, start_time=minute_start, end_time=minute_end)
        day_data.sort(key=lambda x: x.timestamp)
        hour_data.sort(key=lambda x: x.timestamp)
        minute_data.sort(key=lambda x: x.timestamp)
        day_dates = get_dates(day_data)
        day_map = format_day_map(day_data)
        hour_map = format_day_map(hour_data)
        minute_map = format_day_map(minute_data)
        for i in range(negative_day_minute_slope_days, len(minute_map.keys())):
            sub_days = day_dates[i - negative_day_minute_slope_days:i + negative_day_minute_slope_days + negative_month_day_slope_days + positive_month_day_slope_days]
            if len(sub_days) < negative_month_day_slope_days + positive_month_day_slope_days:
                continue
            csv_data += __format_data(stock_code, sub_days, day_map, hour_map, minute_map)
        current = datetime.combine(day_dates[-1], datetime.min.time())
        write_data(csv_data, file)
        write_data(csv_data, f".single/{file}")


def get_current_history_slopes(stock_code: str, month_day_data, week_hour_data, day_minute_data) -> [StockData]:
    month_day_history = []
    week_hour_history = []
    day_minute_history = []
    for bar in month_day_data:
        month_day_history += generate_points(bar)
    for bar in week_hour_data:
        week_hour_history += generate_points(bar)
    for bar in day_minute_data:
        day_minute_history += generate_points(bar)
    month_day_slope = get_slope_in_days(month_day_history, ["PRICE", "TIMESTAMP"])
    week_hour_slope = get_slope_in_minutes(week_hour_history, ["PRICE", "TIMESTAMP"])
    day_minute_slope = get_slope_in_minutes(day_minute_history, ["PRICE", "TIMESTAMP"])
    stock_data = StockData(stock_code)
    stock_data.month_day_slope = month_day_slope
    stock_data.week_hour_slope = week_hour_slope
    stock_data.day_minute_slope = day_minute_slope
    return stock_data






