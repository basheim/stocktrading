from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.base import Job
from apscheduler.triggers.cron import CronTrigger
from lib.auto_trader.v1.manager import orchestrator
from lib.clients.rds_manager import get_stocks

scheduler = BackgroundScheduler()
active_jobs: [Job] = []
background_jobs: [Job] = []


def activate():
    active_jobs.append(
        scheduler.add_job(orchestrator, CronTrigger.from_crontab('0,30 15-20 * * mon-fri', 'utc'), replace_existing=True)
    )
    scheduler.start()


def deactivate():
    job: Job = active_jobs.pop()
    job.remove()


def keep_db_open():
    background_jobs.append(
        scheduler.add_job(get_stocks, CronTrigger.from_crontab('0 * * * *', 'utc'),
                          replace_existing=True)
    )
    scheduler.start()
