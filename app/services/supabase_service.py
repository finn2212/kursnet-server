import logging
from app.config.supabase_config import supabase  # Supabase configuration import
from datetime import datetime

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
    import requests
    from requests.adapters import HTTPAdapter
    from requests.packages.urllib3.util.retry import Retry

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
