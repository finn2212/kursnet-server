from supabase_config import supabase
from datetime import datetime

# Funktion zum Einfügen der Daten in die Supabase-Datenbank mit UPSERT
def insert_data(table_name, data, conflict_column='id'):
    response = supabase.table(table_name).upsert(data, on_conflict=[conflict_column]).execute()
    return response

# Funktion zum Verarbeiten und Einfügen der Daten in Supabase
def process_data(data):
    for item in data['_embedded']['termine']:
        try:
            # Einfügen in "bildungsanbieter"
            anbieter = item['angebot']['bildungsanbieter']
            anbieter_data = {
                "id": anbieter['id'],
                "name": anbieter['name'],
                "telefonvorwahl": anbieter.get('telefonVorwahl', None),
                "telefondurchwahl": anbieter.get('telefondurchwahl', None),
                "homepage": anbieter.get('homepage', None),
                "email": anbieter.get('email', None)
            }
            insert_data("bildungsanbieter", anbieter_data, conflict_column="id")

            # Einfügen in "angebote"
            angebot = item['angebot']
            angebot_data = {
                "id": angebot['id'],
                "titel": angebot['titel'],
                "inhalt": angebot['inhalt'],
                "abschlussart": angebot.get('abschlussart', None),
                "abschlussbezeichnung": angebot.get('abschlussbezeichnung', None),
                "foerderung": angebot.get('foerderung', None),
                "link": angebot.get('link', None),
                "bildungsanbieter_id": anbieter['id']
            }
            insert_data("angebote", angebot_data, conflict_column="id")

            # Konvertiere Zeitstempel (Millisekunden) in ISO-Format
            beginn_timestamp = datetime.utcfromtimestamp(item['beginn'] / 1000).isoformat() if item.get('beginn') else None
            ende_timestamp = datetime.utcfromtimestamp(item['ende'] / 1000).isoformat() if item.get('ende') else None

            # Einfügen in "termine"
            termine_data = {
                "id": item['id'],
                "unterrichtsform_id": item['unterrichtsform']['id'],
                "unterrichtsform_bezeichnung": item['unterrichtsform']['bezeichnung'],
                "unterrichtszeit_id": item['unterrichtszeit']['id'],
                "unterrichtszeit_bezeichnung": item['unterrichtszeit']['bezeichnung'],
                "dauer_id": item['dauer']['id'],
                "dauer_bezeichnung": item['dauer']['bezeichnung'],
                "angebot_id": angebot['id'],
                "beginn": beginn_timestamp,
                "ende": ende_timestamp,
            }

            if 'kostenWertCluster' in item:
                termine_data['kostenwertcluster'] = item.get('kostenWertCluster')
            if 'kostenWwaehrung' in item:
                termine_data['kostenwaehrung'] = item.get('kostenWaehrung')
            if 'foerderung' in item:
                termine_data['foerderung'] = item.get('foerderung')

            insert_data("termine", termine_data, conflict_column="id")
        except Exception as e:
            return {"error": str(e)}
