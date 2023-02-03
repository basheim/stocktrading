from pydantic import ValidationError
from alpaca.common.exceptions import APIError
from flask import Flask, request, Response
from flask_httpauth import HTTPBasicAuth
from lib.clients.rds_manager import insert_stock, delete_stock, get_stock
from lib.clients.secrets_manager import get_secret, Secret
from lib.clients.alpaca_manager import get_current_market_price
from lib.auto_trader.schedule import activate, deactivate, keep_db_open, keep_backend_db_open, start_schedule, running_jobs, build_models
from lib.clients.alpaca_manager import execute_buy, execute_sell, get_order, cancel_order
import json
import logging
from datetime import datetime, timezone
from lib.auto_trader.v2.manager import MLStockModels, orchestrator

auth = HTTPBasicAuth()
app = Flask(__name__)
start_schedule()
keep_db_open(app)
keep_backend_db_open(app)
with app.app_context():
    ml_models = MLStockModels()
    build_models(app, ml_models)
    orchestrator(ml_models)


if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)


@app.get("/py/api/health")
def health():
    return {"status": "healthy"}


@app.post("/py/api/activate")
@auth.login_required()
def activate_method():
    activate(app)
    return {"status": "activation_completed", "jobs": str(running_jobs())}


@app.get("/py/api/jobs")
@auth.login_required()
def get_jobs_method():
    return {"status": "completed", "jobs": str(running_jobs())}


@app.post("/py/api/deactivate")
@auth.login_required()
def deactivate_method():
    deactivate()
    return {"status": "deactivation_completed", "jobs": str(running_jobs())}


@app.delete("/py/api/stock/<stock_id>")
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


@app.post("/py/api/stock")
@auth.login_required()
def add_stock_method():
    body = request.json
    name = body['name']
    code = body['code']
    try:
        get_current_market_price(code)
    except (APIError, ValidationError) as e:
        app.logger.info(str(e))
        return Response(f'{{"error": "Validation Error", "code": "{code}"}}', status=400, mimetype="application/json")
    stock_id = insert_stock(name, code, 0, 0)
    return {"status": "stock_added", "data": stock_id}


@auth.verify_password
def verify_password(username, password):
    secret_json = json.loads(get_secret(Secret.PASSWORD)["SecretString"])
    return username == secret_json["user"] and password == secret_json["password"]
