from app.manager import manager
from flask import current_app
from celery import shared_task
from lib.clients.rds_manager import get_stocks, __db
from lib.clients.backend_manager import get_stocks_backend, get_post_ids_backend
from lib.misc.plant_refresh import refresh_plants
from lib.misc.schedule_wrappers import stock_wrapper, with_function


@shared_task()
def initialize_opening_prices():
    stock_wrapper(current_app, manager.opening_prices.build)


@shared_task()
def initialize_monitors():
    stock_wrapper(current_app, manager.monitors.build)


@shared_task()
def initialize_models():
    stock_wrapper(current_app, manager.models.build)


@shared_task()
def execute_model_reviews():
    stock_wrapper(current_app, manager.orchestrator)


@shared_task()
def execute_monitor_reviews():
    stock_wrapper(current_app, manager.monitor)


@shared_task()
def keep_db_open():
    with_function(current_app, get_stocks)
    with_function(current_app, __db.connect)


@shared_task()
def keep_backend_db_open():
    with_function(current_app, get_stocks_backend)
    with_function(current_app, get_post_ids_backend)


@shared_task()
def refresh_plants_schedule():
    with_function(current_app, refresh_plants)
