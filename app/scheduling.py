from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.base import Job
from apscheduler.triggers.cron import CronTrigger
from lib.routes.tasks import refresh_plants_schedule as refresh_plants_schedule_task, keep_db_open as keep_db_open_task, keep_backend_db_open as keep_backend_db_open_task, initialize_models, initialize_monitors, initialize_opening_prices, execute_model_reviews, execute_monitor_reviews


scheduler = BackgroundScheduler()
active_jobs: [Job] = []
background_jobs: [Job] = []


def activate():
    if len(active_jobs) == 0:
        active_jobs.append(
            scheduler.add_job(initialize_models.delay, CronTrigger.from_crontab('2 13 * * mon-fri', 'utc'), replace_existing=True, name="initialize_models")
        )
        active_jobs.append(
            scheduler.add_job(execute_model_reviews.delay, CronTrigger.from_crontab('45 14 * * mon-fri', 'utc'), replace_existing=True, name="model_review_1")
        )
        active_jobs.append(
            scheduler.add_job(execute_model_reviews.delay, CronTrigger.from_crontab('7 15 * * mon-fri', 'utc'), replace_existing=True, name="model_review_2")
        )
        active_jobs.append(
            scheduler.add_job(initialize_opening_prices.delay, CronTrigger.from_crontab('35 14 * * mon-fri', 'utc'), replace_existing=True, name="initialize_opening_prices")
        )
        active_jobs.append(
            scheduler.add_job(execute_monitor_reviews.delay, CronTrigger.from_crontab('0,15,30,45 15-20 * * mon-fri', 'utc'), replace_existing=True, name="monitor_review")
        )
        active_jobs.append(
            scheduler.add_job(initialize_monitors.delay, CronTrigger.from_crontab('0 13 * * mon-fri', 'utc'), replace_existing=True, name="initialize_monitors")
        )


def deactivate():
    for _ in range(len(active_jobs)):
        job: Job = active_jobs.pop()
        scheduler.remove_job(job.id)


def running_jobs():
    return scheduler.get_jobs()


def keep_db_open():
    background_jobs.append(
        scheduler.add_job(keep_db_open_task.delay, CronTrigger.from_crontab('25 * * * *', 'utc'),
                          replace_existing=True, name="keep_db_open")
    )


def keep_backend_db_open():
    background_jobs.append(
        scheduler.add_job(keep_backend_db_open_task.delay, CronTrigger.from_crontab('22 * * * *', 'utc'),
                          replace_existing=True, name="keep_backend_db_open")
    )


def refresh_plants_schedule():
    background_jobs.append(
        scheduler.add_job(refresh_plants_schedule_task.delay, CronTrigger.from_crontab('20 * * * *', 'utc'),
                          replace_existing=True, name="refresh_plant_schedule")
    )


def start_schedule():
    scheduler.start()
