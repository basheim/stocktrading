from alpaca.data import Quote
from alpaca.data.models import Bar
from datetime import datetime


class HistoryAssessment:
    long_term: [Bar]
    short_term: [Bar]
    current: Quote
    columns: [str, str]
    short_term_data: [[float, datetime]]
    long_term_data: [[float, datetime]]
    code: str
    assessment: bool
    short_slope: float
    med_slope: float
    long_slope: float

    @staticmethod
    def build(long_term: [Bar], short_term: [Bar], current: Quote, code: str):
        long_term_data = []
        short_term_data = []
        for bar in long_term:
            long_term_data.append([bar.low, bar.timestamp])
            long_term_data.append([bar.open, bar.timestamp])
            long_term_data.append([bar.close, bar.timestamp])
            long_term_data.append([bar.high, bar.timestamp])
        for bar in short_term:
            short_term_data.append([bar.low, bar.timestamp])
            short_term_data.append([bar.open, bar.timestamp])
            short_term_data.append([bar.close, bar.timestamp])
            short_term_data.append([bar.high, bar.timestamp])
        long_term_data.append([current.ask_price, current.timestamp])
        short_term_data.append([current.ask_price, current.timestamp])
        return HistoryAssessment(long_term, short_term, current, code, False, long_term_data, short_term_data)

    def __init__(self, long_term: [Bar], short_term: [Bar], current: Quote, code: str, assessment: bool, long_term_data: [[float, str]], short_term_data: [[float, str]]):
        self.long_term = long_term
        self.short_term = short_term
        self.current = current
        self.code = code
        self.assessment = assessment
        self.long_term_data = long_term_data
        self.short_term_data = short_term_data
        self.columns = ["PRICE", "TIME"]
        self.short_slope = 0
        self.med_slope = 0
        self.long_slope = 0

    def __repr__(self):
        return str(
            {
                "code": self.code,
                "short": self.short_slope,
                "med": self.med_slope,
                "long": self.long_slope,
                "assessment": self.assessment
            }
        )
