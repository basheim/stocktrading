import numpy as np
import pandas as pd
from lib.auto_trader.history_assessment import HistoryAssessment
from datetime import datetime


def set_predictions(assessment: HistoryAssessment):
    columns = assessment.columns
    assessment.short_slope = __get_slope(assessment.short_term_data[:10], columns)
    assessment.med_slope = __get_slope(assessment.short_term_data, columns)
    assessment.long_slope = __get_slope(assessment.long_term_data, columns)


def __get_slope(data: [[float, datetime]], columns: [str, str]):
    start_date = data[0][1]
    start_price = data[0][0]
    df = pd.DataFrame(data=data, columns=columns)
    df['TIME'] = pd.to_datetime(df['TIME'])
    df_plot = pd.DataFrame()
    df_plot['HOURS'] = (df['TIME'] - pd.to_datetime(start_date)).dt.seconds / (60 * 60)
    df_plot['PERCENT'] = (pd.to_numeric(df['PRICE']) / pd.to_numeric(start_price)) * 100
    f = np.polyfit(df_plot['HOURS'], df_plot['PERCENT'], deg=1)
    return f[0]
