from datetime import datetime


class Transaction:
    transaction_id: str
    stock_id: str
    name: str
    action: str
    quantity: float
    price: float
    date: datetime

    @staticmethod
    def build(sql_data: {}):
        return Transaction(
            sql_data["id"],
            sql_data["stockId"],
            sql_data["name"],
            sql_data["action"],
            sql_data["quantity"],
            sql_data["price"],
            sql_data["date"]
        )

    def __init__(self, transaction_id:str, stock_id: str, name: str, action: str, quantity: float, price: float, date: datetime):
        self.transaction_id = transaction_id
        self.stock_id = stock_id
        self.name = name
        self.action = action
        self.quantity = quantity
        self.price = price
        self.date = date
