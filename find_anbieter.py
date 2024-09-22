from flask import Blueprint, request, jsonify, Response
import requests
from supabase_config import supabase  # Deine Supabase-Konfiguration importieren
from datetime import datetime
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# Blueprint für die find-anbieter-Route
find_anbieter_bp = Blueprint('find_anbieter', __name__)

# Funktion zum Einfügen der Daten in die Supabase-Datenbank mit UPSERT
def insert_data(table_name, data, conflict_column='id'):
    response = supabase.table(table_name).upsert(data, on_conflict=[conflict_column]).execute()
    logging.info(f"Inserted data into table {table_name}: {data}")  # Logge den Insert-Status
    return response

# Funktion zum Verarbeiten und Einfügen der Anbieter-Daten in Supabase
def process_anbieter_data(anbieter):
    try:
        anbieter_data = {
            "id": anbieter['id'],
            "name": anbieter['name'],
            "telefonvorwahl": anbieter.get('telefonVorwahl', None),
            "telefondurchwahl": anbieter.get('telefondurchwahl', None),
            "homepage": anbieter.get('homepage', None),
            "email": anbieter.get('email', None)
        }
        insert_data("bildungsanbieter", anbieter_data, conflict_column="id")
    except Exception as e:
        logging.error(f"Error processing anbieter data: {str(e)}")
        return {"error": str(e)}

# Funktion zum Abrufen von Daten für eine Anbieter-ID mit Retry-Mechanismus
def fetch_anbieter_data(anbieter_id, clientId, base_url, headers, retries=3):
    params = {"ban": anbieter_id}
    logging.info(f"Fetching data for Anbieter-ID: {anbieter_id}")
    
    retry_strategy = Retry(
        total=retries,  # Anzahl der Wiederholungen
        status_forcelist=[429, 500, 502, 503, 504],  # Fehler-Codes, bei denen wiederholt wird
        method_whitelist=["GET"],  # Nur für GET-Methoden anwenden
        backoff_factor=1  # Wartezeit zwischen den Wiederholungen (z.B. 1 Sekunde, 2 Sekunden, usw.)
    )
    
    adapter = HTTPAdapter(max_retries=retry_strategy)
    http = requests.Session()
    http.mount("https://", adapter)

    try:
        response = http.get(base_url, headers=headers, params=params, timeout=30)  # Timeout auf 30 Sekunden erhöht
        if response.status_code == 200:
            data = response.json()
            if data and '_embedded' in data:
                try:
                    anbieter = data['_embedded']['termine'][0]['angebot']['bildungsanbieter']
                    process_anbieter_data(anbieter)
                    return f"Anbieter-ID {anbieter_id}: Daten erfolgreich verarbeitet."
                except (IndexError, KeyError):
                    return f"Anbieter-ID {anbieter_id}: Keine gültigen Daten gefunden."
            else:
                return f"Anbieter-ID {anbieter_id}: Keine Daten gefunden."
        else:
            return f"Anbieter-ID {anbieter_id}: Fehler beim Abrufen der Daten (Statuscode: {response.status_code})."
    
    except requests.exceptions.ReadTimeout:
        return f"Anbieter-ID {anbieter_id}: Timeout-Fehler."

# Neue Route /find-anbieter mit Parallelisierung und Retry
@find_anbieter_bp.route('/find-anbieter', methods=['GET'])
def find_anbieter():
    def event_stream(start_id, end_id):
        clientId = "infosysbub-wbsuche"
        base_url = "https://rest.arbeitsagentur.de/infosysbub/wbsuche/pc/v2/bildungsangebot"
        headers = {"X-API-Key": clientId}

        last_successful_id = None  # Speichert die letzte erfolgreiche Anbieter-ID
        max_workers = 10  # Anzahl gleichzeitiger Threads für parallele Anfragen
        
        # Thread-Pool für parallele Verarbeitung
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            for anbieter_id in range(start_id, end_id + 1):
                # Ein Task pro Anbieter-ID im Pool starten
                futures.append(executor.submit(fetch_anbieter_data, anbieter_id, clientId, base_url, headers))

            # Verarbeitung der Futures, sobald sie fertig sind
            for future in as_completed(futures):
                result = future.result()
                yield f"data: {result}\n\n"
                logging.info(result)

        yield "data: Verarbeitung abgeschlossen.\n\n"

    try:
        # Parameter (ID-Bereich) aus der Anfrage abrufen
        start_id = int(request.args.get('start_id'))
        end_id = int(request.args.get('end_id'))

        # Rückgabe als Event-Stream
        return Response(event_stream(start_id, end_id), content_type='text/event-stream')

    except Exception as e:
        logging.error(f"Error in find_anbieter: {str(e)}")
        return jsonify({"error": str(e)}), 500
