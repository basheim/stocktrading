from flask import Flask
from flask_httpauth import HTTPBasicAuth
from lib.clients.secrets_manager import get_secret, Secret
from lib.clients.alpaca_manager import get_positions
import json

auth = HTTPBasicAuth()
app = Flask(__name__)


@app.get("/py/api/health")
def health():
    return {"status": "healthy"}


"""
 Comment in to test
"""
@app.get("/py/api/test")
def test():
    return str(get_positions())


@app.post("/py/api/activate")
@auth.login_required()
def activate():
    return {"status": "activation_completed"}


@app.post("/py/api/deactivate")
@auth.login_required()
def deactivate():
    return {"status": "deactivation_completed"}


@auth.verify_password
def verify_password(username, password):
    secret_json = json.loads(get_secret(Secret.PASSWORD)["SecretString"])
    return username == secret_json["user"] and password == secret_json["password"]
