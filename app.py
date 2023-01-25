from flask import Flask
from flask_httpauth import HTTPBasicAuth
from lib.secrets_manager import get_secret, Secret
import json
auth = HTTPBasicAuth()

app = Flask(__name__)


@app.get("/py/api/health")
def health():
    return {"status": "healthy"}


@app.post("/py/api/activate")
@auth.login_required()
def activate():
    pass


@app.post("/py/api/deactivate")
@auth.login_required()
def deactivate():
    pass


@auth.verify_password
def verify_password(username, password):
    secret_json = json.loads(get_secret(Secret.DB)["SecretString"])
    return username == secret_json["user"] and password == secret_json["password"]
