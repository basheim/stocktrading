from lib.clients.secrets_manager import Secret, get_secret
from lib.objects.sql_data import SqlData
from lib.objects.stock import Stock
from lib.objects.transaction import Transaction
from lib.objects.selected_plant import SelectedPlant
from uuid import uuid4
from datetime import datetime
import mysql.connector
import json


class DBConnection:
    def __init__(self, host: str, user: str, password: str, database: str):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        self.cursor = None

    def connect(self):
        self.connection = mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database
        )
        self.cursor = self.connection.cursor(buffered=True)


__arn = "arn:aws:rds:us-west-2:796569311964:cluster:beans-sql-db"
secret_json = json.loads(get_secret(Secret.DB)["SecretString"])
__db = DBConnection(
    host="beans-sql-db.clj2unssy8o7.us-west-2.rds.amazonaws.com",
    user=secret_json["username"],
    password=secret_json["password"],
    database="monolith"
)
__db.connect()


"""
Test Code
"""
CURRENT_ACCOUNT_ID = "testCurrent"

"""
Real Code
CURRENT_ACCOUNT_ID = "current"
"""


def update_account(amount: float) -> None:
    __commit_sql(
        "UPDATE account_status SET amount=%s WHERE id=%s;",
        tuple([amount, CURRENT_ACCOUNT_ID])
    )


def insert_transaction(stock_id: str, price: float, quantity: float, name: str, action: str, date: datetime) -> None:
    __commit_sql(
        "INSERT INTO stock_transactions (id,stockId,name,quantity,price,action,date) VALUES (%s, %s, %s, %s, %s, %s, %s);",
        tuple([str(uuid4()), stock_id, name, quantity, price, action, str(date)])
    )


def get_transactions() -> [Transaction]:
    transactions = __fetch_sql(
        "SELECT * FROM stock_transactions;"
    )
    return [Transaction.build(x) for x in transactions.data]


def delete_transaction(transaction_id: str) -> None:
    __commit_sql(
        "DELETE FROM stock_transactions WHERE id=%s;",
        tuple([transaction_id])
    )


def get_selected_plants() -> [SelectedPlant]:
    plants = __fetch_sql(
        "SELECT * FROM selected_plants;"
    )
    return [SelectedPlant.build(x) for x in plants.data]


def update_selected_plant(plant_id: str, start: datetime, end: datetime):
    __commit_sql(
        "UPDATE selected_plants SET start=%s, end=%s WHERE id=%s;",
        tuple([plant_id, str(start), str(end)])
    )


def get_stocks() -> [Stock]:
    stocks = __fetch_sql(
        "SELECT * FROM stocks;"
    )
    return [Stock.build(x) for x in stocks.data]


def update_stock(stock_id: str, quantity: float, price: float) -> None:
    __commit_sql(
        "UPDATE stocks SET quantity=%s, price=%s WHERE id=%s;",
        tuple([quantity, price, stock_id])
    )


def insert_stock(name: str, code: str, quantity: float, price: float) -> str:
    stock_id = str(uuid4())
    __commit_sql(
        "INSERT INTO stocks (id,name,code,quantity,price) VALUES (%s, %s, %s, %s, %s);",
        tuple([stock_id, name, code, quantity, price])
    )
    return stock_id


def delete_stock(stock_id: str) -> None:
    __commit_sql(
        "DELETE FROM stocks WHERE id=%s;",
        tuple([stock_id])
    )


def get_stock(stock_id: str) -> Stock:
    stocks = __fetch_sql(
        "SELECT * FROM stocks WHERE id=%s;",
        tuple([stock_id])
    ).data
    if len(stocks) == 0:
        return Stock.build({})
    return [Stock.build(x) for x in stocks][0]


def __commit_sql(sql: str, parameters: [] = ()) -> None:
    __db.cursor.execute(sql, parameters)
    __db.connection.commit()


def __fetch_sql(sql: str, parameters: [] = ()) -> SqlData:
    __db.cursor.execute(sql, parameters)
    try:
        columns = __db.cursor.column_names
        responses = __db.cursor.fetchall()
        data = []
        for response in responses:
            temp = {}
            for i in range(len(columns)):
                temp[columns[i]] = response[i]
            data.append(temp)
    except mysql.connector.errors.InterfaceError:
        columns = []
        data = []
    return SqlData(columns, data)


