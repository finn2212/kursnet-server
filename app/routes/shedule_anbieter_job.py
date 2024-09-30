from flask import Blueprint, request, jsonify, Response
import requests
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from app.jobs.anbieter_job import find_anbieter, start_find_anbieter_manually, schedule_find_anbieter_job
import threading

# Blueprint für die find-anbieter-Route
shedule_anbieter_job_bp = Blueprint('shedule_anbieter_job', __name__)

# Route to manually trigger the Anbieter job
@shedule_anbieter_job_bp.route('/manual-anbieter-job', methods=['POST'])
def manual_anbieter_job():
    try:
        data = request.get_json()
        start_id = data.get('start_id', 1000)
        end_id = data.get('end_id', 2000)

        # Start the job in a separate thread
        job_thread = threading.Thread(target=start_find_anbieter_manually, args=(start_id, end_id))
        job_thread.start()

        # Return response immediately without waiting for the job to complete
        return jsonify({"status": "Job started manually", "start_id": start_id, "end_id": end_id}), 200

    except Exception as e:
        logging.error(f"Error in manual_anbieter_job: {str(e)}")
        return jsonify({"error": str(e)}), 500
