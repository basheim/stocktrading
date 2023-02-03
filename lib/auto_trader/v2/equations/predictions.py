import numpy as np
import pandas as pd
from lib.objects.history_assessment import HistoryAssessment
from datetime import datetime


def get_slope_in_hours(data: [[float, datetime]], columns: [str, str]):
    start_date = data[0][1]
    start_price = data[0][0]
    df = pd.DataFrame(data=data, columns=columns)
    df[columns[1]] = pd.to_datetime(df[columns[1]])
    df_plot = pd.DataFrame()
    df_plot['HOURS'] = (df[columns[1]] - pd.to_datetime(start_date)).dt.seconds / (60 * 60)
    df_plot['PERCENT'] = (pd.to_numeric(df[columns[0]]) / pd.to_numeric(start_price)) * 100
    f = np.polyfit(df_plot['HOURS'], df_plot['PERCENT'], deg=1)
    return f[0]


def get_slope_in_minutes(data: [[float, datetime]], columns: [str, str]):
    start_date = data[0][1]
    start_price = data[0][0]
    df = pd.DataFrame(data=data, columns=columns)
    df[columns[1]] = pd.to_datetime(df[columns[1]])
    df_plot = pd.DataFrame()
    df_plot['MINUTES'] = (df[columns[1]] - pd.to_datetime(start_date)).dt.seconds / 60
    df_plot['PERCENT'] = (pd.to_numeric(df[columns[0]]) / pd.to_numeric(start_price)) * 100
    f = np.polyfit(df_plot['MINUTES'], df_plot['PERCENT'], deg=1)
    return f[0]
