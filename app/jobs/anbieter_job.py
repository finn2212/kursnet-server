import requests
from supabase_config import supabase  # Supabase configuration import
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import time

# Global variables for the scheduler and job reference
scheduler = None
find_anbieter_job = None

# Function to insert data into Supabase
def insert_data(table_name, data, conflict_column='id'):
    response = supabase.table(table_name).upsert(data, on_conflict=[conflict_column]).execute()
    logging.info(f"Inserted data into table {table_name}: {data}")
    return response

# Function to log job results in the Supabase job_logs table
def log_job_result(job_name, counters, job_duration, status, job_type):
    job_data = {
        "job_name": job_name,
        "new_ids": counters['new_ids'],
        "updated_ids": counters['updated_ids'],
        "timeouts": counters['timeouts'],
        "passed_ids": counters['passed_ids'],
        "job_duration": job_duration,
        "status": status,
        "job_date": datetime.utcnow().isoformat(),
        "job_type": job_type  # "manual" or "scheduled"
    }
    supabase.table("job_logs").insert(job_data).execute()
    logging.info(f"Logged job result: {job_data}")

# Function to process and insert anbieter data into Supabase
def process_anbieter_data(anbieter, counters):
    try:
        anbieter_data = {
            "id": anbieter['id'],
            "name": anbieter['name'],
            "telefonvorwahl": anbieter.get('telefonVorwahl', None),
            "telefondurchwahl": anbieter.get('telefondurchwahl', None),
            "homepage": anbieter.get('homepage', None),
            "email": anbieter.get('email', None)
        }
        result = insert_data("bildungsanbieter", anbieter_data, conflict_column="id")
        logging.info(f"Anbieter successfully processed: {str(result)}")
        counters['new_ids'] += 1
        logging.info(f"New Anbieter count: {str(counters['new_ids'])}")
    except Exception as e:
        logging.error(f"Error processing anbieter data: {str(e)}")
        return {"error": str(e)}

# Function to fetch Anbieter data with retry mechanism
def fetch_anbieter_data(anbieter_id, clientId, base_url, headers, counters, retries=5):
    params = {"ban": anbieter_id}
    logging.info(f"Fetching data for Anbieter-ID: {anbieter_id}")
    
    retry_strategy = Retry(
        total=retries,
        status_forcelist=[429, 500, 502, 503, 504],
        method_whitelist=["GET"],
        backoff_factor=5
    )
    
    adapter = HTTPAdapter(max_retries=retry_strategy)
    http = requests.Session()
    http.mount("https://", adapter)

    try:
        response = http.get(base_url, headers=headers, params=params, timeout=30)
        if response.status_code == 200:
            data = response.json()
            if data and '_embedded' in data:
                try:
                    anbieter = data['_embedded']['termine'][0]['angebot']['bildungsanbieter']
                    process_anbieter_data(anbieter, counters)
                    return f"Anbieter-ID {anbieter_id}: Daten erfolgreich verarbeitet."
                except (IndexError, KeyError):
                    return f"Anbieter-ID {anbieter_id}: Keine gültigen Daten gefunden."
            else:
                return f"Anbieter-ID {anbieter_id}: Keine Daten gefunden."
        else:
            return f"Anbieter-ID {anbieter_id}: Fehler beim Abrufen der Daten (Statuscode: {response.status_code})."
    
    except requests.exceptions.ReadTimeout:
        counters['timeouts'] += 1
        return f"Anbieter-ID {anbieter_id}: Timeout-Fehler."

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
