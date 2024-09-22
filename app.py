from flask import Flask, jsonify
from fetch_data import get_data_from_page
from save_data import process_data
from count_pages import count_pages_bp  # Importiere das Blueprint
from find_anbieter import find_anbieter_bp  # Importiere das find-anbieter Blueprint
from flask_cors import CORS  # Importiere Flask-CORS

app = Flask(__name__)

# CORS für alle Routen und nur für localhost:3000 erlauben
CORS(app, resources={r"/*": {"origins": ["http://localhost:3000"]}}, supports_credentials=True)

# Registriere die Blueprints
app.register_blueprint(count_pages_bp)
app.register_blueprint(find_anbieter_bp)

# Route für die Startseite
@app.route('/')
def home():
    return "Welcome to the API! Use the /process_data, /count-pages, or /find-anbieter endpoint to interact with the API."

# Flask-Endpunkt für die Verarbeitung der Daten aus der API
@app.route('/process_data', methods=['GET'])
def handle_request():
    try:
        page = 0
        size = 20

        # Abrufen der Daten von der API
        data = get_data_from_page(page, size)

        if "error" in data:
            return jsonify({"error": data['error']})

        # Verarbeitung der Daten
        process_data(data)
        return jsonify({"message": f"Seite {page} wurde erfolgreich verarbeitet."})
    
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(debug=True)
