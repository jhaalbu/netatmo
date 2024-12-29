import sqlite3
import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

client_id = r'677185976af826b5950079c2'
client_secret = r'HofmdX0LBi0G7zKh0HL0qyMzY4m'

access_token = "67718565925e7647a10954ee|85288ba2ea2b9d803aaa52c9750f5a4a"
refresh_token = "67718565925e7647a10954ee|197cdf17722a4a1bf849b0c3a5552ecc"

headers = {"Authorization": f"Bearer {access_token}"}


# Grenser
nord_øst_lat = 63.0
nord_øst_lon = 13.0
sør_vest_lat = 58.0
sør_vest_lon = 5.0

# Rutestørrelse
breddegrad_steg = 0.25  # Juster for finere rutenett
lengdegrad_steg = 0.5



# Opprett SQLite-database
conn = sqlite3.connect("weather_data.db")
cursor = conn.cursor()

# Opprett tabeller
cursor.execute("""
CREATE TABLE IF NOT EXISTS weather_stations (
    station_id TEXT PRIMARY KEY,
    city TEXT,
    street TEXT,
    latitude REAL,
    longitude REAL,
    altitude REAL,
    country TEXT,
    timezone TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS measurements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    station_id TEXT,
    module_id TEXT,
    measurement_type TEXT,
    measurement_time INTEGER,
    value REAL,
    FOREIGN KEY(station_id) REFERENCES weather_stations(station_id)
)
""")

# Liste for ruter
ruter = []

# Generer ruter
breddegrad = sør_vest_lat
while breddegrad < nord_øst_lat:
    lengdegrad = sør_vest_lon
    while lengdegrad < nord_øst_lon:
        rute = {
            "lat_ne": breddegrad + breddegrad_steg,
            "lon_ne": lengdegrad + lengdegrad_steg,
            "lat_sw": breddegrad,
            "lon_sw": lengdegrad,
        }
        ruter.append(rute)
        lengdegrad += lengdegrad_steg
    breddegrad += breddegrad_steg

# Funksjon for å hente data for en rute
def hent_data_for_rute(rute):
    lat_ne = rute["lat_ne"]
    lon_ne = rute["lon_ne"]
    lat_sw = rute["lat_sw"]
    lon_sw = rute["lon_sw"]

    url = f'https://api.netatmo.com/api/getpublicdata?lat_ne={lat_ne}&lon_ne={lon_ne}&lat_sw={lat_sw}&lon_sw={lon_sw}&required_data=rain&filter=true'

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            #print(response.json())
            return response.json()["body"]
        else:
            #print(response.json())
            return []
    except Exception as e:
        print(f"Feil under API-kall for rute {rute}: {e}")
        return []

# Funksjon for å lagre data i databasen
def lagre_data(data):
    for station in data:
        station_id = station["_id"]
        place = station["place"]
        latitude, longitude = place["location"]
        city = place.get("city")
        street = place.get("street")
        altitude = place.get("altitude")
        country = place.get("country")
        timezone = place.get("timezone")

        # Sett inn værstasjon
        cursor.execute("""
        INSERT OR IGNORE INTO weather_stations (
            station_id, city, street, latitude, longitude, altitude, country, timezone
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (station_id, city, street, latitude, longitude, altitude, country, timezone))

        # Sett inn målinger
        measures = station["measures"]
        for module_id, measure_data in measures.items():
            if "res" in measure_data:
                for timestamp, values in measure_data["res"].items():
                    for measurement_type, value in zip(measure_data["type"], values):
                        cursor.execute("""
                        INSERT INTO measurements (
                            station_id, module_id, measurement_type, measurement_time, value
                        ) VALUES (?, ?, ?, ?, ?)
                        """, (station_id, module_id, measurement_type, timestamp, value))
            else:
                for key, value in measure_data.items():
                    if key.endswith("timeutc"):
                        timestamp = value
                    elif isinstance(value, (int, float)):
                        measurement_type = key
                        cursor.execute("""
                        INSERT INTO measurements (
                            station_id, module_id, measurement_type, measurement_time, value
                        ) VALUES (?, ?, ?, ?, ?)
                        """, (station_id, module_id, measurement_type, timestamp, value))

# Parallell behandling av API-kall
with ThreadPoolExecutor(max_workers=10) as executor:
    fremtid_til_rute = {executor.submit(hent_data_for_rute, rute): rute for rute in ruter}

    for fremtid in as_completed(fremtid_til_rute):
        data = fremtid.result()
        lagre_data(data)

# Lagre og lukk tilkobling
conn.commit()
conn.close()

print("Data lagret i SQLite-databasen.")
