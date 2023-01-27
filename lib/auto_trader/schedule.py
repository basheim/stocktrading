from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.base import Job
from apscheduler.triggers.cron import CronTrigger
from lib.auto_trader.v1.manager import orchestrator

scheduler = BackgroundScheduler()
active_jobs: [Job] = []


def activate():
    active_jobs.append(
        scheduler.add_job(orchestrator, CronTrigger.from_crontab('0,30 15-20 * * mon-fri', 'utc'), replace_existing=True)
    )
    scheduler.start()


def deactivate():
    job: Job = active_jobs.pop()
    job.remove()
