from flask import Flask
from lib.rds_manager import get_stocks, delete_stock, post_stock
from datetime import datetime, timezone

app = Flask(__name__)


@app.get("/py/api/health")
def health():
    return {"status": "healthy"}


@app.get("/py/api/test")
def stocks_post():
    post_stock("test", "t", 120, 5, datetime.now(timezone.utc))
    return []