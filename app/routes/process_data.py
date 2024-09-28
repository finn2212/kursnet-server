from flask import Blueprint, jsonify
from app.services.save_data import  process_data
from app.fetch_data import get_data_from_page

process_data_bp = Blueprint('process_data', __name__)

@process_data_bp.route('/process_data', methods=['GET'])
def handle_request():
    try:
        page = 0
        size = 20
        data = get_data_from_page(page, size)

        if "error" in data:
            return jsonify({"error": data['error']})

        process_data(data)
        return jsonify({"message": f"Seite {page} wurde erfolgreich verarbeitet."})
    
    except Exception as e:
        return jsonify({"error": str(e)})
