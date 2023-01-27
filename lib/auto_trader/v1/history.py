from alpaca.data import Quote
from alpaca.data.models import Bar
from lib.objects.history_assessment import HistoryAssessment
from lib.auto_trader.v1.equations.predictions import set_predictions
from lib.objects.stock import Stock


def create_histories(long_term: {str: [Bar]}, short_term: {str: [Bar]},  current: {str: Quote}, stocks: [Stock]) -> {str: HistoryAssessment}:
    assessments = build_assessments(long_term, short_term, current, stocks)
    for assessment in assessments.values():
        set_predictions(assessment)
    return assessments


def build_assessments(long_term: {str: [Bar]}, short_term: {str: [Bar]}, current: {str: Quote}, stocks: [Stock]) -> {str: HistoryAssessment}:
    assessments = {}
    for stock in stocks:
        assessments[stock.code] = HistoryAssessment.build(long_term[stock.code], short_term[stock.code], current[stock.code], stock)
    return assessments

