from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.base import Job
from apscheduler.triggers.cron import CronTrigger
from lib.clients.rds_manager import get_stocks, __db
from lib.auto_trader.v3.manager import orchestrator, monitor, opening_price
from lib.clients.backend_manager import get_stocks_backend
from lib.misc.plant_refresh import refresh_plants
from flask import current_app
from pandas_market_calendars import get_calendar, date_range
from datetime import datetime, timedelta
from pytz import timezone

scheduler = BackgroundScheduler()
active_jobs: [Job] = []
background_jobs: [Job] = []


def activate(app, ml_models):
    with_function(app, ml_models.build_models)
    with_function(app, opening_price, tuple([ml_models]))
    active_jobs.append(
        scheduler.add_job(lambda: stock_wrapper(app, ml_models.build_models), CronTrigger.from_crontab('0 13 * * mon-fri', 'utc'), replace_existing=True)
    )
    active_jobs.append(
        scheduler.add_job(lambda: stock_wrapper(app, orchestrator, tuple([ml_models])), CronTrigger.from_crontab('0 15 * * mon-fri', 'utc'), replace_existing=True)
    )
    active_jobs.append(
        scheduler.add_job(lambda: stock_wrapper(app, opening_price, tuple([ml_models])), CronTrigger.from_crontab('33 14 * * mon-fri', 'utc'), replace_existing=True)
    )
    active_jobs.append(
        scheduler.add_job(lambda: stock_wrapper(app, monitor, tuple([ml_models])), CronTrigger.from_crontab('15,30,45 15-20 * * mon-fri', 'utc'), replace_existing=True)
    )
    active_jobs.append(
        scheduler.add_job(lambda: stock_wrapper(app, monitor, tuple([ml_models])), CronTrigger.from_crontab('45 14 * * mon-fri', 'utc'), replace_existing=True)
    )


def deactivate():
    for _ in range(len(active_jobs)):
        job: Job = active_jobs.pop()
        scheduler.remove_job(job.id)


def running_jobs():
    return scheduler.get_jobs()


def keep_db_open(app):
    background_jobs.append(
        scheduler.add_job(lambda: with_function(app, get_stocks), CronTrigger.from_crontab('45 * * * *', 'utc'),
                          replace_existing=True)
    )


def refresh_connections(app):
    background_jobs.append(
        scheduler.add_job(lambda: with_function(app, __db.connect), CronTrigger.from_crontab('15 * * * *', 'utc'),
                          replace_existing=True)
    )


def keep_backend_db_open(app):
    background_jobs.append(
        scheduler.add_job(lambda: with_function(app, get_stocks_backend), CronTrigger.from_crontab('20 * * * *', 'utc'),
                          replace_existing=True)
    )


def refresh_plants_schedule(app):
    background_jobs.append(
        scheduler.add_job(lambda: with_function(app, refresh_plants), CronTrigger.from_crontab('30 * * * *', 'utc'),
                          replace_existing=True)
    )


def start_schedule():
    scheduler.start()


def with_function(app, func, passed_args=tuple()):
    with app.app_context():
        current_app.logger.info(f"Background function: ${func.__name__}")
        func(*passed_args)


def stock_wrapper(app, func, passed_args=tuple()):
    d1 = datetime.today() - timedelta(days=1)
    d2 = datetime.today() + timedelta(days=1)
    nyse = get_calendar('NYSE')
    open_date_range = nyse.schedule(start_date=d1, end_date=d2)
    dates = date_range(open_date_range, frequency='1D')
    now = datetime.now(tz=timezone('UTC'))
    for date in dates:
        converted_date = datetime.fromisoformat(str(date))
        if converted_date.day == now.day and now < converted_date:
            with_function(app, func, passed_args)
            break
