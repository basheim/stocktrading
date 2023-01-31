from lib.clients.secrets_manager import Secret, get_secret
import json
from requests import request


secret_json = json.loads(get_secret(Secret.PASSWORD)["SecretString"])


def get_stocks_backend():
    res = request(
        method="GET",
        url="https://backend.programmingbean.com/api/v1/stocks"
    )
    return res.json()
