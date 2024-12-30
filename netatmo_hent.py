import requests
import pprint
import pandas as pd
import json
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import time
import csv
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime



client_id = r'677185976af826b5950079c2'
client_secret = r'HofmdX0LBi0G7zKh0HL0qyMzY4m'

access_token = "67718565925e7647a10954ee|b501c010545ff03969d96394b5415de4"
refresh_token = "67718565925e7647a10954ee|790342fde81c4fd7a603d1414676e23c"

headers = {"Authorization": f"Bearer {access_token}"}

response = requests.get(f'https://api.netatmo.com/api/getpublicdata?lat_ne=61.99&lon_ne=8.99&lat_sw=60.0&lon_sw=5.0&required_data=rain&filter=true', headers=headers)
data = response.json()
# Grenser
nord_øst_lat = 63.0
nord_øst_lon = 13.0
sør_vest_lat = 58.0
sør_vest_lon = 5.0

# nord_øst_lat = 61.25
# nord_øst_lon = 7.14
# sør_vest_lat = 61.20
# sør_vest_lon = 7.05

# Rutestørrelse
breddegrad_steg = 0.25  # Endre til mindre for finere ruter
lengdegrad_steg = 0.5

# Liste for å lagre rutene
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

# Funksjon for å gjøre API-kall
def hent_data_for_rute(rute):
    lat_ne = rute["lat_ne"]
    lon_ne = rute["lon_ne"]
    lat_sw = rute["lat_sw"]
    lon_sw = rute["lon_sw"]

    url = f'https://api.netatmo.com/api/getpublicdata?lat_ne={lat_ne}&lon_ne={lon_ne}&lat_sw={lat_sw}&lon_sw={lon_sw}&required_data=rain&filter=true'

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return data.get("body", [])  # Returner kun kroppsdelen med data
        else:
            return []  # Returner tom liste ved feil
    except Exception as e:
        print(f"Feil under henting av data: {e}")
        return []

# Funksjon for å hente ut nedbør, temperatur, og stasjonsinformasjon
def filtrer_nedbor_og_temperatur(data):
    filtrerte_data = []
    for stasjon in data:
        stasjon_id = stasjon.get("_id", "")
        location = stasjon.get("place", {}).get("location", [])
        altitude = stasjon.get("place", {}).get("altitude", None)

        nedbor_24h = None
        nedbor_60min = None
        temperatur = None

        # Finn nedbør
        for modul_id, modul_data in stasjon.get("measures", {}).items():
            if nedbor_24h is None and "rain_24h" in modul_data:
                nedbor_24h = modul_data.get("rain_24h")
                nedbor_60min = modul_data.get("rain_60min")
                tidspunkt = modul_data.get("rain_timeutc")

        # Finn temperatur (kan være i en annen modul)
        for modul_id, modul_data in stasjon.get("measures", {}).items():
            if temperatur is None and 'temperature' in modul_data.get('type', []):
                temperatur = list(modul_data['res'].values())[0][0]

        # Legg til data hvis nedbør finnes
        if nedbor_24h is not None:
            filtrerte_data.append({
                "stasjon_id": stasjon_id,
                "tidspunkt": tidspunkt,
                "location": location,
                "altitude": altitude,
                "nedbor_24h": nedbor_24h,
                "nedbor_60min": nedbor_60min,
                "temperatur": temperatur
            })

    return filtrerte_data

# Lagre filtrerte data til CSV
def lagre_til_csv(filnavn, data):
    with open(filnavn, mode='w', newline='', encoding='utf-8') as fil:
        writer = csv.writer(fil)
        writer.writerow(["stasjon_id", "location", "tidspunkt", "altitude", "nedbor_24h", "nedbor_60min", "temperatur"])
        for rad in data:
            writer.writerow([
                rad["stasjon_id"], 
                rad["location"], 
                rad["tidspunkt"],
                rad["altitude"], 
                rad["nedbor_24h"], 
                rad["nedbor_60min"], 
                rad["temperatur"]
            ])

# Parallell behandling av ruter
resultater = []
start_time = time.time()

with ThreadPoolExecutor(max_workers=10) as executor:  # Juster antall tråder etter behov
    fremtid_til_rute = {executor.submit(hent_data_for_rute, rute): rute for rute in ruter}

    for fremtid in as_completed(fremtid_til_rute):
        data = fremtid.result()
        filtrerte = filtrer_nedbor_og_temperatur(data)
        resultater.extend(filtrerte)

#print(resultater)
# Lagre filtrerte data til CSV-fil
filnavn = f'resultater_{datetime.now().strftime("%H_%M_%S")}.csv'
lagre_til_csv(filnavn, resultater)

print(f"Ferdig! Filtrerte resultater lagret til '{filnavn}'. Kjøringstid: {time.time() - start_time:.2f} sekunder")