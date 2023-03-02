import subprocess
import csv
from math import inf
from datetime import datetime, timedelta, date
from alpaca.data.models import Bar


def generate_base_files(headers: [str]):
    subprocess.run("rm -rf ./.tmp/.tmp_data || true".split())
    subprocess.run("mkdir ./.tmp/.tmp_data".split())
    subprocess.run("touch ./.tmp/.tmp_data/raw_data.csv".split())
    with open('./.tmp/.tmp_data/raw_data.csv', 'w', encoding='UTF8') as f:
        writer = csv.writer(f)
        # write the header
        writer.writerow(headers)


def delete_all_files():
    subprocess.run("rm -rf ./.tmp/.tmp_data || true".split())


def write_data(csv_data: [any], file: str):
    with open(f'./.tmp/.tmp_data/{file}', 'a', encoding='UTF8') as f:
        writer = csv.writer(f)

        for row in csv_data:
            # write the data
            writer.writerow(row.get_as_row())


def generate_points(bar: Bar):
    temp = []
    if bar and bar.high and bar.timestamp and bar.high != inf:
        temp.append([bar.high, bar.timestamp])
    if bar and bar.low and bar.timestamp and bar.low != inf:
        temp.append([bar.low, bar.timestamp])
    return temp


def generate_single_files(headers: [str]):
    subprocess.run("rm -rf ./.tmp/.tmp_data/.single || true".split())
    subprocess.run("mkdir ./.tmp/.tmp_data/.single".split())
    subprocess.run("touch ./.tmp/.tmp_data/.single/raw_data.csv".split())
    with open('./.tmp/.tmp_data/.single/raw_data.csv', 'w', encoding='UTF8') as f:
        writer = csv.writer(f)
        # write the header
        writer.writerow(headers)


def decrement_stock_hours(d: datetime, hours: int):
    for _ in range(hours):
        d -= timedelta(hours=1)
        while not is_stock_day(d):
            d -= timedelta(hours=1)
    return d


def decrement_stock_days(d: datetime, days: int):
    for _ in range(days):
        d -= timedelta(days=1)
        while not is_stock_day(d):
            d -= timedelta(days=1)
    return d


def increment_stock_days(d: datetime, days: int):
    for _ in range(days):
        d += timedelta(days=1)
        while not is_stock_day(d):
            d += timedelta(days=1)
    return d


def is_stock_day(d: datetime):
    return d.weekday() != 5 and d.weekday() != 6


def format_day_map(data: [Bar]):
    temp = {}
    for x in data:
        d = x.timestamp.date()
        if d not in temp:
            temp[d] = []
        temp[d].append(x)
    return temp


def format_hour_map(data: [Bar]):
    temp = {}
    for x in data:
        d = x.timestamp.date()
        h = x.timestamp.hour
        if d not in temp:
            temp[d] = {}
        if h not in temp[d]:
            temp[d][h] = []
        temp[d][h].append(x)
    return temp


def get_dates(data: [Bar]) -> [date]:
    temp = []
    for x in data:
        d = x.timestamp.date()
        if (len(temp) == 0 or temp[-1] != d) and is_stock_day(d):
            temp.append(d)
    return temp
