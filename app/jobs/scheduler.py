from apscheduler.schedulers.background import BackgroundScheduler
from app.jobs.anbieter_job import find_anbieter

def schedule_jobs():
    scheduler = BackgroundScheduler()

    # Schedule Anbieter job
    scheduler.add_job(
        func=find_anbieter,
        trigger='cron',
        args=[1000, 2000],  # Example range for IDs
        hour=3,  # Run daily at 3 AM
        id='find_anbieter_job',
        replace_existing=True
    )

    scheduler.start()
