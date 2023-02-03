from lib.auto_trader.v2.history import write_complete_history


def orchestrator():
    test_stock_id = "ef607e45-6005-493a-b9e3-b836c5e4f452"
    write_complete_history(test_stock_id)