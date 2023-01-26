from alpaca.data import Quote
from alpaca.data.models import Bar
from lib.auto_trader.history_assessment import HistoryAssessment
from lib.auto_trader.math_v1.predictions import set_predictions


MONTH_SLOPE_MIN = -10
WEEK_SLOPE_MIN = 0.05
SHORT_TERM_SLOPE_MIN = 0.05


def assess_histories(long_term: {str: [Bar]}, short_term: {str: [Bar]},  current: {str: Quote}, codes: [str]) -> [HistoryAssessment]:
    assessments = build_assessments(long_term, short_term, current, codes)
    for assessment in assessments:
        assess_history(assessment)
    return assessments


def build_assessments(long_term: {str: [Bar]}, short_term: {str: [Bar]}, current: {str: Quote}, codes: [str]) -> [HistoryAssessment]:
    assessments = []
    for code in codes:
        assessments.append(HistoryAssessment.build(long_term[code], short_term[code], current[code], code))
    return assessments


def assess_history(assessment: HistoryAssessment):
    set_predictions(assessment)
    if assessment.short_slope >= SHORT_TERM_SLOPE_MIN and assessment.med_slope >= WEEK_SLOPE_MIN and assessment.long_slope >= MONTH_SLOPE_MIN:
        assessment.assessment = True
