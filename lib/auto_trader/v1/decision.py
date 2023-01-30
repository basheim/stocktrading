from lib.objects.history_assessment import HistoryAssessment


MONTH_SLOPE_MIN = -10
WEEK_SLOPE_MIN = 0.01
SHORT_TERM_SLOPE_MIN = 0.1
MINIMUM_SELL = 0.95


def should_buy(assessment: HistoryAssessment):
    return not __owned(assessment) and __has_slope(assessment)


def should_sell(assessment: HistoryAssessment):
    return __owned(assessment) and (__has_downward_slope(assessment) or __value_too_low(assessment))


def __value_too_low(assessment: HistoryAssessment):
    return assessment.current.ask_price <= (MINIMUM_SELL * assessment.owned_price)


def __has_downward_slope(assessment: HistoryAssessment):
    return assessment.short_slope < 0


def __owned(assessment: HistoryAssessment):
    return assessment.owned != 0.0


def __has_slope(assessment: HistoryAssessment):
    return assessment.short_slope >= SHORT_TERM_SLOPE_MIN and \
           assessment.med_slope >= WEEK_SLOPE_MIN and \
           assessment.long_slope >= MONTH_SLOPE_MIN
