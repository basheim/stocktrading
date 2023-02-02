from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.base import Job
from apscheduler.triggers.cron import CronTrigger
from lib.auto_trader.v1.manager import orchestrator
from lib.clients.rds_manager import get_stocks
from lib.clients.backend_manager import get_stocks_backend
from flask import current_app

scheduler = BackgroundScheduler()
active_jobs: [Job] = []
background_jobs: [Job] = []


def activate(app):
    active_jobs.append(
        scheduler.add_job(lambda: with_function(app, orchestrator), CronTrigger.from_crontab('0,30 15-20 * * mon-fri', 'utc'), replace_existing=True)
    )
    active_jobs.append(
        scheduler.add_job(lambda: with_function(app, orchestrator), CronTrigger.from_crontab('35 14 * * mon-fri', 'utc'), replace_existing=True)
    )
    active_jobs.append(
        scheduler.add_job(lambda: with_function(app, orchestrator), CronTrigger.from_crontab('55 20 * * mon-fri', 'utc'), replace_existing=True)
    )


def deactivate():
    for _ in range(len(active_jobs)):
        job: Job = active_jobs.pop()
        scheduler.remove_job(job.id)


def running_jobs():
    return scheduler.get_jobs()


def keep_db_open(app):
    background_jobs.append(
        scheduler.add_job(lambda: with_function(app, get_stocks), CronTrigger.from_crontab('0 * * * *', 'utc'),
                          replace_existing=True)
    )


def keep_backend_db_open(app):
    background_jobs.append(
        scheduler.add_job(lambda: with_function(app, get_stocks_backend), CronTrigger.from_crontab('0 * * * *', 'utc'),
                          replace_existing=True)
    )


def start_schedule():
    scheduler.start()


def with_function(app, func):
    with app.app_context():
        current_app.logger.info(f"Background function: ${func.__name__}")
        func()
