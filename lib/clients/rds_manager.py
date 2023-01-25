from lib.clients.secrets_manager import Secret, get_secret
from uuid import uuid4
from datetime import datetime
import mysql.connector
import json

__arn = "arn:aws:rds:us-west-2:796569311964:cluster:beans-sql-db"
secret_json = json.loads(get_secret(Secret.DB)["SecretString"])
__db = mysql.connector.connect(
            host="beans-sql-db.clj2unssy8o7.us-west-2.rds.amazonaws.com",
            user=secret_json["username"],
            password=secret_json["password"],
            database="monolith"
        )
__db_cursor = __db.cursor(buffered=True)


class SqlData:
    columns: []
    data: []

    def __init__(self, columns, data):
        self.data = data
        self.columns = columns


def update_account(account_id: str, amount: int) -> None:
    __commit_sql(
        "UPDATE account_status SET amount=%s WHERE id=%s;",
        tuple([amount, account_id])
    )


def insert_transaction(stock_id: str, price: int, quantity: int, name: str, action: str, date: datetime) -> None:
    __commit_sql(
        "INSERT INTO stock_transactions (id,stock_id,name,quantity,price,action,date) VALUES (%s, %s, %s, %s, %s, %s, %s);",
        tuple([str(uuid4()), stock_id, name, quantity, price, action, str(date)])
    )


def get_stocks() -> SqlData:
    return __fetch_sql(
        "SELECT * FROM stocks;"
    )


def update_stock(stock_id: str, quantity: int) -> None:
    __commit_sql(
        "UPDATE stocks SET quantity=%s WHERE id=%s;",
        tuple([quantity, stock_id])
    )


def insert_stock(name: str, code: str, quantity: int) -> None:
    __commit_sql(
        "INSERT INTO stocks (id,name,code,quantity) VALUES (%s, %s, %s, %s);",
        tuple([str(uuid4()), name, code, quantity])
    )


def delete_stock(stock_id: str) -> None:
    __commit_sql(
        "DELETE FROM stocks WHERE id=%s;",
        tuple([stock_id])
    )


def __commit_sql(sql: str, parameters: [] = ()) -> None:
    __db_cursor.execute(sql, parameters)
    __db.commit()


def __fetch_sql(sql: str, parameters: [] = ()) -> SqlData:
    __db_cursor.execute(sql, parameters)
    try:
        columns = __db_cursor.column_names
        responses = __db_cursor.fetchall()
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


