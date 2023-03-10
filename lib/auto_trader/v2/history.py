import uuid
from datetime import datetime, date
from lib.clients.alpaca_manager import get_historical_market_price, Steps
from lib.auto_trader.generic.equations.predictions import get_slope_in_hours, get_slope_in_minutes
from lib.auto_trader.generic.helpers import generate_single_files, generate_points, increment_stock_days, decrement_stock_days, format_day_map, format_hour_map, get_dates, write_data


negative_hour_range = 7
positive_hour_range = 3
negative_minute_range = 1
positive_minute_range = 0


class StockData:
    row_id: str
    stock_code: str
    hour_minute_slope: float
    day_minute_slope: float
    week_hour_slope: float
    state: str

    def __init__(self, stock_code: str):
        self.stock_code = stock_code
        self.row_id = str(uuid.uuid4())
        self.hour_minute_slope = 0
        self.day_minute_slope = 0
        self.week_hour_slope = 0
        self.state = "sell"

    @staticmethod
    def build(stock_data):
        temp = StockData(stock_data.stock_id)
        temp.week_hour_slope = stock_data.week_hour_slope
        temp.day_minute_slope = stock_data.day_minute_slope
        temp.hour_minute_slope = stock_data.hour_minute_slope
        temp.state = stock_data.state
        return temp

    @staticmethod
    def get_headers():
        return ["hour_minute_slope", "day_minute_slope", "week_hour_slope", "state"]

    def get_as_num_row(self):
        return [self.hour_minute_slope, self.day_minute_slope, self.week_hour_slope]

    def get_as_row(self):
        return [str(self.hour_minute_slope), str(self.day_minute_slope), str(self.week_hour_slope), str(self.state)]

    def __repr__(self):
        return str({
            "row_id": self.row_id,
            "stock_code": self.stock_code,
            "hour_minute_slope": self.hour_minute_slope,
            "day_minute_slope": self.day_minute_slope,
            "week_hour_slope": self.week_hour_slope,
            "state": self.state
        })


def __format_data(stock_code: str, dates: [date], hour_data: any, minute_data: any) -> [StockData]:
    complete_data = []
    hour_history = []
    minute_day_history = []
    for i in range(7):
        temp = hour_data[dates[i]]
        for bar in temp:
            hour_history += generate_points(bar)
    bars = []
    if dates[6] not in minute_data:
        return complete_data
    for hour_minute_data in minute_data[dates[6]].values():
        bars += hour_minute_data
    bars.sort(key=lambda x: x.timestamp)
    for bar in bars:
        minute_day_history += generate_points(bar)
    current = dates[7]
    for i in range(1, len(hour_data[current])):
        index = i * 2
        new_hour_history = []
        new_minute_history = []
        new_minute_hour_history = []
        minute_count = 0
        for j in range(i):
            new_hour_history += generate_points(hour_data[current][j])
            if current in minute_data and hour_data[current][j].timestamp.hour in minute_data[current]:
                for bar in minute_data[current][hour_data[current][j].timestamp.hour]:
                    new_minute_history += generate_points(bar)
                    if j == i - 1:
                        new_minute_hour_history += generate_points(bar)
        for k in range(0, index, 2):
            hour = hour_history[k][1].hour
            while len(minute_day_history) > minute_count and hour == minute_day_history[minute_count][1].hour:
                minute_count += 1
        temp_hour_history = hour_history[index:] + new_hour_history
        temp_minute_day_history = minute_day_history[minute_count:] + new_minute_history
        hour_slope = get_slope_in_hours(temp_hour_history, ["PRICE", "TIMESTAMP"])
        if len(temp_minute_day_history) < 12:
            continue
        minute_day_slope = get_slope_in_minutes(temp_minute_day_history, ["PRICE", "TIMESTAMP"])
        if len(new_minute_hour_history) < 8:
            continue
        minute_hour_slope = get_slope_in_minutes(new_minute_hour_history, ["PRICE", "TIMESTAMP"])
        base_stock_data = StockData(stock_code)
        base_stock_data.week_hour_slope = hour_slope
        base_stock_data.day_minute_slope = minute_day_slope
        base_stock_data.hour_minute_slope = minute_hour_slope
        # buy = (hour_data[current][i].high + hour_data[current][i].low) / 2
        buy = hour_data[current][i].open
        # pointer = 1
        # sell_aggregate = 0
        # for sell_data in range(i + 1, len(hour_data[current])):
        #     sell = (hour_data[current][sell_data].high + hour_data[current][sell_data].low) / 2
        #     sell_aggregate += sell
        #     pointer += 1
        # for date_pointer in range(8, 10):
        #     for sell_data in range(0, len(hour_data[dates[date_pointer]])):
        #         sell = (hour_data[dates[date_pointer]][sell_data].high + hour_data[dates[date_pointer]][sell_data].low) / 2
        #         sell_aggregate += sell
        #         pointer += 1
        # profit = (sell_aggregate / (pointer - 1)) - buy
        # 1 day
        # if i + 1 < len(hour_data[current]):
        #     sell = (hour_data[current][i + 1].high + hour_data[current][i + 1].low) / 2
        # else:
        #     sell = (hour_data[dates[8]][0].high + hour_data[dates[8]][0].low) / 2

        if i + 1 < len(hour_data[current]):
            sell = hour_data[current][i + 1].open
        else:
            sell = hour_data[dates[8]][0].open
        # end of next day
        # sell = (hour_data[dates[8]][-1].high + hour_data[dates[8]][-1].low) / 2
        profit = sell - buy
        state = "sell"
        if profit > 0:
            state = "buy"
        base_stock_data.state = state
        complete_data.append(base_stock_data)
    return complete_data


def write_complete_history(stock_id: str) -> None:
    generate_single_files(StockData.get_headers())
    __write_complete_history_helper(stock_id, 30, 1, "raw_data.csv")


def __write_complete_history_helper(stock_code: str, start: int, end: int, file: str) -> None:
    start = decrement_stock_days(datetime.today().replace(hour=0, minute=0, second=0, microsecond=0), start)
    current = start
    end = decrement_stock_days(datetime.today().replace(hour=0, minute=0, second=0, microsecond=0), end)
    step = 21

    while increment_stock_days(current, positive_hour_range) < end:
        csv_data = []
        hour_start = decrement_stock_days(current, negative_hour_range)
        minute_start = decrement_stock_days(current, negative_minute_range)
        temp_end = increment_stock_days(current, step + positive_hour_range)
        while temp_end >= end:
            temp_end = decrement_stock_days(temp_end, 1)
        hour_end = temp_end
        minute_end = increment_stock_days(decrement_stock_days(temp_end, positive_hour_range), positive_minute_range)
        if minute_start >= minute_end or hour_start >= hour_end:
            break
        hour_data = get_historical_market_price(code=stock_code, step=Steps.HOUR, start_time=hour_start, end_time=hour_end)
        minute_data = get_historical_market_price(code=stock_code, step=Steps.MINUTE, start_time=minute_start, end_time=minute_end)
        hour_data.sort(key=lambda x: x.timestamp)
        minute_data.sort(key=lambda x: x.timestamp)
        hour_dates = get_dates(hour_data)
        hour_map = format_day_map(hour_data)
        minute_map = format_hour_map(minute_data)
        for i in range(len(minute_map.keys()) - (negative_minute_range + positive_minute_range)):
            if len(hour_dates[i:i + negative_hour_range + positive_hour_range]) < negative_hour_range + positive_hour_range:
                continue
            csv_data += __format_data(stock_code, hour_dates[i:i + negative_hour_range + positive_hour_range], hour_map, minute_map)
        current = datetime.combine(hour_dates[-2], datetime.min.time())
        write_data(csv_data, file)
        write_data(csv_data, f".single/{file}")


def get_current_history_slopes(stock_code: str, hour_data, minute_day_data, minute_hour_data) -> [StockData]:
    hour_history = []
    minute_day_history = []
    minute_hour_history = []
    for bar in hour_data:
        hour_history += generate_points(bar)
    for bar in minute_day_data:
        minute_day_history += generate_points(bar)
    for bar in minute_hour_data:
        minute_hour_history += generate_points(bar)
    hour_slope = get_slope_in_hours(hour_history, ["PRICE", "TIMESTAMP"])
    minute_day_slope = get_slope_in_minutes(minute_day_history, ["PRICE", "TIMESTAMP"])
    minute_hour_slope = get_slope_in_minutes(minute_hour_history, ["PRICE", "TIMESTAMP"])
    stock_data = StockData(stock_code)
    stock_data.week_hour_slope = hour_slope
    stock_data.day_minute_slope = minute_day_slope
    stock_data.hour_minute_slope = minute_hour_slope
    return stock_data






