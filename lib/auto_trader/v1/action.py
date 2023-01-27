from lib.objects.history_assessment import HistoryAssessment
from lib.clients.alpaca_manager import execute_buy, execute_sell
from lib.clients.rds_manager import update_stock, insert_transaction
from pydantic import ValidationError
from alpaca.common.exceptions import APIError
from decimal import Decimal, ROUND_DOWN
from flask import current_app


def buy(assessment: HistoryAssessment, account: float):
    current_app.logger.info(f"Buy transaction for {assessment.code} started...")
    try:
        order = execute_buy(assessment.code, float(Decimal(account / assessment.current.ask_price).quantize(Decimal('.001'), rounding=ROUND_DOWN)))
    except (APIError, ValidationError) as e:
        current_app.logger.error("Unable to execute buy action")
        return
    assessment.owned = order.filled_qty
    assessment.owned_price = order.filled_avg_price
    update_stock(assessment.stock_id, assessment.owned, assessment.owned_price)
    insert_transaction(assessment.stock_id, assessment.owned_price, assessment.owned, assessment.name, "buy", order.created_at)
    current_app.logger.info(f"Buy transaction for {assessment.code} completed with quantity {assessment.owned} and price {assessment.owned_price}")


def sell(assessment: HistoryAssessment):
    current_app.logger.info(f"Sell transaction for {assessment.code} started...")
    try:
        order = execute_sell(assessment.code, assessment.owned)
    except (APIError, ValidationError) as e:
        current_app.logger.error("Unable to execute sell action")
        return

    update_stock(assessment.stock_id, 0, 0)
    insert_transaction(assessment.stock_id, order.filled_avg_price, order.filled_qty, assessment.name, "sell",
                       order.created_at)
    current_app.logger.info(
        f"Sell transaction for {assessment.code} completed with quantity {order.filled_qty} and price {order.filled_avg_price}")
    assessment.owned = 0
    assessment.owned_price = 0