import requests

# API-Anfrage
clientId = "infosysbub-wbsuche"
base_url = "https://rest.arbeitsagentur.de/infosysbub/wbsuche/pc/v2/bildungsangebot"
headers = {"X-API-Key": clientId}

def get_data_from_page(page, size=20):
    url = f"{base_url}?page={page}&size={size}"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"Fehler: {response.status_code} - {response.text}"}
