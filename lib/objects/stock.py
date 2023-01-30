class Stock:
    stock_id: str
    code: str
    name: str
    quantity: float
    price: float

    @staticmethod
    def build(sql_data: []):
        return Stock(
            sql_data["id"],
            sql_data["code"],
            sql_data["name"],
            sql_data["quantity"],
            sql_data["price"]
        )

    def __init__(self, stock_id: str, code: str, name: str, quantity: float, price: float):
        self.stock_id = stock_id
        self.code = code
        self.name = name
        self.quantity = quantity
        self.price = price
