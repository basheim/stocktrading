from lib.objects.history_assessment import HistoryAssessment
from lib.clients.alpaca_manager import execute_buy, execute_sell, get_order, cancel_order
from lib.clients.rds_manager import update_stock, insert_transaction
from pydantic import ValidationError
from alpaca.common.exceptions import APIError
from time import sleep
from decimal import Decimal, ROUND_DOWN
from flask import current_app


def buy(assessment: HistoryAssessment, account: float):
    current_app.logger.info(f"Buy transaction for {assessment.code} started...")
    price = assessment.current.ask_price
    qty = float(Decimal(account / price).quantize(Decimal('.01'), rounding=ROUND_DOWN))
    try:
        order = execute_buy(assessment.code, qty)
        order_id = order.id
    except (APIError, ValidationError) as e:
        current_app.logger.error(str(e))
        current_app.logger.error("Unable to execute buy action")
        return
    try:
        completed_order = None
        count = 0
        while not completed_order and count < 30:
            temp = get_order(order_id)
            if temp.status == 'filled':
                completed_order = temp
            else:
                sleep(1)
                count += 1
        if not completed_order:
            cancel_order(order_id)
            raise APIError("Order was not filled in time")
    except (APIError, ValidationError) as e:
        current_app.logger.error(str(e))
        current_app.logger.error("Unable to complete buy order")
        return
    assessment.owned = completed_order.filled_qty
    assessment.owned_price = completed_order.filled_avg_price
    update_stock(assessment.stock_id, assessment.owned, assessment.owned_price)
    insert_transaction(assessment.stock_id, assessment.owned_price, assessment.owned, assessment.name, "buy", completed_order.created_at)
    current_app.logger.info(f"Buy transaction for {assessment.code} completed with quantity {assessment.owned} and price {assessment.owned_price}")


def sell(assessment: HistoryAssessment):
    current_app.logger.info(f"Sell transaction for {assessment.code} started...")
    try:
        order = execute_sell(assessment.code, assessment.owned)
        order_id = order.id
    except (APIError, ValidationError) as e:
        current_app.logger.error(str(e))
        current_app.logger.error("Unable to execute sell action")
        return
    try:
        completed_order = None
        count = 0
        while not completed_order and count < 30:
            temp = get_order(order_id)
            if temp.status == 'filled':
                completed_order = temp
            else:
                sleep(1)
                count += 1
        if not completed_order:
            cancel_order(order_id)
            raise APIError("Order was not filled in time")
    except (APIError, ValidationError) as e:
        current_app.logger.error(str(e))
        current_app.logger.error("Unable to complete sell order")
        return
    update_stock(assessment.stock_id, 0, 0)
    insert_transaction(assessment.stock_id, completed_order.filled_avg_price, completed_order.filled_qty, assessment.name, "sell",
                       completed_order.created_at)
    current_app.logger.info(
        f"Sell transaction for {assessment.code} completed with quantity {order.filled_qty} and price {order.filled_avg_price}")
    assessment.owned = 0
    assessment.owned_price = 0