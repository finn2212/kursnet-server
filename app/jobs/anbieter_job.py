from concurrent.futures import ThreadPoolExecutor, as_completed
from apscheduler.schedulers.background import BackgroundScheduler
import time
import logging
from app.services.supabase_service import fetch_anbieter_data, log_job_result

# Global variables for the scheduler and job reference
scheduler = None
find_anbieter_job = None

# Function to execute the task for a range of Anbieter IDs with detailed logging
def find_anbieter(start_id, end_id, job_type="manual"):
    clientId = "infosysbub-wbsuche"
    base_url = "https://rest.arbeitsagentur.de/infosysbub/wbsuche/pc/v2/bildungsangebot"
    headers = {"X-API-Key": clientId}

    max_workers = 20  # Number of concurrent threads
    counters = {'new_ids': 0, 'updated_ids': 0, 'timeouts': 0, 'passed_ids': 0}  # Dictionary to track counters
    start_time = time.time()  # Start job timer
    results = []

    # Thread pool for parallel processing
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for anbieter_id in range(start_id, end_id + 1):
            futures.append(executor.submit(fetch_anbieter_data, anbieter_id, clientId, base_url, headers, counters))

        # Process results as they are completed
        for future in as_completed(futures):
            result = future.result()
            counters['passed_ids'] += 1  # Every ID processed counts as passed
            results.append(result)
            logging.info(result)
    
    job_duration = time.time() - start_time  # Job duration in seconds
    logging.info("Verarbeitung abgeschlossen.")

    # Log the job result
    log_job_result(
        job_name="anbieter_job",
        counters=counters,
        job_duration=job_duration,
        status="completed" if counters['timeouts'] == 0 else "completed_with_errors",
        job_type=job_type  # Log whether job was manual or scheduled
    )

    return results

# Function to schedule the job with APScheduler
def schedule_find_anbieter_job(start_id, end_id):
    global scheduler, find_anbieter_job

    # Create a background scheduler if not already started
    if scheduler is None:
        scheduler = BackgroundScheduler()
        scheduler.start()

    # Schedule the job at a specific interval (e.g., daily at 3 AM)
    find_anbieter_job = scheduler.add_job(
        func=find_anbieter,
        trigger='cron',
        args=[start_id, end_id, "scheduled"],  # Mark the job as "scheduled"
        hour=3,  # Time to execute
        minute=0,
        id='find_anbieter_job',
        replace_existing=True
    )

    logging.info(f"Job scheduled to run daily at 3 AM for IDs from {start_id} to {end_id}")

# Function to manually start the job
def start_find_anbieter_manually(start_id, end_id):
    # Manually trigger the function without scheduling
    logging.info(f"Manually starting the job for IDs from {start_id} to {end_id}")
    find_anbieter(start_id, end_id, "manual")  # Mark the job as "manual"
