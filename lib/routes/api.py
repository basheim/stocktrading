from pydantic import ValidationError
from alpaca.common.exceptions import APIError
from flask import request, Response, Blueprint, current_app
from app.manager import manager
from flask_httpauth import HTTPBasicAuth
from lib.clients.rds_manager import insert_stock, delete_stock, get_stock, get_stocks, update_stock, get_transactions, delete_transaction, update_account
from lib.clients.secrets_manager import get_secret, Secret
from lib.clients.alpaca_manager import get_current_market_price
from lib.clients.alpaca_manager import execute_sell
import json
from datetime import datetime, timezone
from lib.routes.tasks import initialize_models, initialize_monitors, initialize_opening_prices, execute_model_reviews
from app.scheduling import activate, deactivate, running_jobs, start_schedule, refresh_plants_schedule, keep_db_open, keep_backend_db_open


auth = HTTPBasicAuth()
routes = Blueprint('routes', __name__)


@routes.get("/py/api/health")
def health():
    return {"status": "healthy"}


@routes.post("/py/api/force/models")
@auth.login_required()
def force_models_method():
    result = initialize_models.delay()
    return {"status": "done", "id": result.id}


@routes.post("/py/api/force/monitors")
@auth.login_required()
def force_monitors_method():
    result = initialize_monitors.delay()
    return {"status": "done", "id": result.id}


@routes.post("/py/api/force/opening_prices")
@auth.login_required()
def force_opening_price_method():
    result = initialize_opening_prices.delay()
    return {"status": "done", "id": result.id}


@routes.post("/py/api/force/run")
@auth.login_required()
def force_run_method():
    result = execute_model_reviews.delay()
    return {"status": "done", "id": result.id}


@routes.post("/py/api/activate")
@auth.login_required()
def activate_method():
    start_schedule()
    keep_backend_db_open()
    keep_db_open()
    refresh_plants_schedule()
    activate()
    return {"status": "activation_completed", "jobs": str(running_jobs())}


@routes.get("/py/api/jobs")
@auth.login_required()
def get_jobs_method():
    return {"status": "completed", "jobs": str(running_jobs())}


@routes.post("/py/api/deactivate")
@auth.login_required()
def deactivate_method():
    deactivate()
    return {"status": "deactivation_completed", "jobs": str(running_jobs())}


@routes.get("/py/api/models")
@auth.login_required()
def get_models_method():
    if manager.opening_prices.has_redis_data():
        manager.opening_prices.load()
    if manager.monitors.has_redis_data():
        manager.monitors.load()
    if manager.models.has_redis_data():
        manager.models.load()
    return {"status": "completed", "manager": str(manager)}


@routes.delete("/py/api/stock/<stock_id>")
@auth.login_required()
def delete_stock_method(stock_id):
    stock = get_stock(stock_id)
    if stock and stock.quantity > 0:
        now = datetime.now(timezone.utc)
        if now.hour >= 21 or now.hour < 14 or (now.hour == 14 and now.minute < 30):
            return {"status": "stock_not_deleted_due_to_time"}
        try:
            execute_sell(stock.code, stock.quantity)
        except (APIError, ValidationError) as e:
            return {"status": "stock_not_deleted_due_to_api_errors"}
    delete_stock(stock_id)
    return {"status": "stock_delete"}


@routes.delete("/py/api/reset/stocks")
@auth.login_required()
def reset_stocks():
    stocks = get_stocks()
    for stock in stocks:
        current_app.logger.info(f"Resetting stock {stock.code}")
        update_stock(stock.stock_id, 0, 0)
    return {"status": "all_stocks_reset"}


@routes.delete("/py/api/transactions")
@auth.login_required()
def delete_all_transactions():
    transactions = get_transactions()
    current_app.logger.info("Deleting all transactions")
    for transaction in transactions:
        delete_transaction(transaction.transaction_id)
    return {"status": "all transactions_deleted"}


@routes.put("/py/api/account")
@auth.login_required()
def update_account_amount():
    body = request.json
    amount = body['amount']
    update_account(amount)
    return {"status": "updated_account"}


@routes.post("/py/api/stock")
@auth.login_required()
def add_stock_method():
    body = request.json
    name = body['name']
    code = body['code']
    try:
        get_current_market_price(code)
    except (APIError, ValidationError) as e:
        current_app.logger.info(str(e))
        return Response(f'{{"error": "Validation Error", "code": "{code}"}}', status=400, mimetype="application/json")
    stock_id = insert_stock(name, code, 0, 0)
    return {"status": "stock_added", "data": stock_id}


@auth.verify_password
def verify_password(username, password):
    secret_json = json.loads(get_secret(Secret.PASSWORD)["SecretString"])
    return username == secret_json["user"] and password == secret_json["password"]
