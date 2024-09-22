from flask import Blueprint, request, jsonify
import requests

# Blueprint für die count_pages-Route
count_pages_bp = Blueprint('count_pages', __name__)

# Funktion zum Abrufen der Seitenanzahl
@count_pages_bp.route('/count-pages', methods=['GET'])
def count_pages():
    try:
        # Standardparameter für die Seitenanzahl
        params = {
            "page": 0,  # Immer Seite 0 für die Seitenermittlung
            "size": 20  # Standardgröße
        }

        # Liste der möglichen Filter
        possible_filters = ['sys', 'sw', 'ssw', 'ids', 'orte', 'uk', 'ortsunabhaengig', 're', 'bt', 'uz', 'dauer', 'uf', 'ban', 'it', 'bg', 'sort']

        # Alle Filterparameter aus der Anfrage übernehmen
        for filter_name in possible_filters:
            if request.args.get(filter_name):
                params[filter_name] = request.args.get(filter_name)

        # Anfrage an die API senden
        clientId = "infosysbub-wbsuche"
        base_url = "https://rest.arbeitsagentur.de/infosysbub/wbsuche/pc/v2/bildungsangebot"
        headers = {"X-API-Key": clientId}

        response = requests.get(base_url, headers=headers, params=params)

        if response.status_code == 200:
            data = response.json()
            total_pages = data.get('page', {}).get('totalPages', 0)
            total_elements = data.get('page', {}).get('totalElements', 0)
            
            # Sende sowohl die API-Antwort als auch die berechneten Werte zurück
            return jsonify({
                "total_pages": total_pages,
                "total_elements": total_elements,
                "full_response": data  # Das gesamte API-Objekt wird hier zurückgegeben
            })
        else:
            return jsonify({"error": f"Fehler: {response.status_code} - {response.text}"}), response.status_code

    except Exception as e:
        return jsonify({"error": str(e)})
