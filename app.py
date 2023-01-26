from pydantic import ValidationError
from alpaca.common.exceptions import APIError
from flask import Flask, request, Response
from flask_httpauth import HTTPBasicAuth
from lib.clients.rds_manager import insert_stock, delete_stock
from lib.clients.secrets_manager import get_secret, Secret
from lib.clients.alpaca_manager import get_current_market_price
from lib.auto_trader.manager import orchestrator
from lib.auto_trader.schedule import activate, deactivate, active_jobs
import json

auth = HTTPBasicAuth()
app = Flask(__name__)


@app.get("/py/api/health")
def health():
    return {"status": "healthy"}


@app.post("/py/api/activate")
@auth.login_required()
def activate_method():
    activate()
    return {"status": "activation_completed", "jobs": str(active_jobs)}


@app.post("/py/api/deactivate")
@auth.login_required()
def deactivate_method():
    deactivate()
    return {"status": "deactivation_completed", "jobs": str(active_jobs)}


@app.delete("/py/api/stock/<stock_id>")
@auth.login_required()
def delete_stock_method(stock_id):
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
    except (APIError, ValidationError):
        return Response(f'{{"error": "Validation Error", "code": "{code}"}}', status=400, mimetype="application/json")
    stock_id = insert_stock(name, code, 0)
    return {"status": "stock_added", "data": stock_id}


@app.get("/py/api/bars")
def tester():
    return str(orchestrator())


@auth.verify_password
def verify_password(username, password):
    secret_json = json.loads(get_secret(Secret.PASSWORD)["SecretString"])
    return username == secret_json["user"] and password == secret_json["password"]
