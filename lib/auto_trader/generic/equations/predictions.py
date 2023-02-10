import numpy as np
import pandas as pd
from datetime import datetime
from enum import Enum


class SlopeStep(Enum):
    MINUTE = 1,
    HOUR = 2,
    DAY = 3


def get_slope_in_days(data: [[float, datetime]], columns: [str, str]):
    return __get_slope(data, columns, SlopeStep.DAY)


def get_slope_in_hours(data: [[float, datetime]], columns: [str, str]):
    return __get_slope(data, columns, SlopeStep.HOUR)


def get_slope_in_minutes(data: [[float, datetime]], columns: [str, str]):
    return __get_slope(data, columns, SlopeStep.MINUTE)


def __get_slope(data: [[float, datetime]], columns: [str, str], step: SlopeStep):
    label = "UNKNOWN"
    div = 1
    match step:
        case SlopeStep.MINUTE:
            label = "MINUTES"
            div = 60
        case SlopeStep.HOUR:
            label = "HOURS"
            div = 60 * 60
        case SlopeStep.DAY:
            label = "DAYS"
            div = 60 * 60 * 24

    start_date = data[0][1]
    start_price = data[0][0]
    df = pd.DataFrame(data=data, columns=columns)
    df[columns[1]] = pd.to_datetime(df[columns[1]])
    start_time = pd.to_datetime(start_date)
    df_plot = pd.DataFrame()
    df_plot[label] = ((df[columns[1]] - start_time) // pd.Timedelta('1s')) / div
    df_plot['PERCENT'] = (pd.to_numeric(df[columns[0]]) / pd.to_numeric(start_price)) * 100
    f = np.polyfit(df_plot[label], df_plot['PERCENT'], deg=1)
    return f[0]
