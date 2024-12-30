import csv
import os
from collections import defaultdict

def compare_station_ids(csv_files):
    station_id_files = defaultdict(set)

    # Les stasjon_id fra hver fil og lagre dem i et sett
    for csv_file in csv_files:
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                station_id_files[csv_file].add(row['stasjon_id'])

    # Finn felles stasjon_id mellom alle filer
    common_station_ids = set.intersection(*station_id_files.values())

    # Skriv ut antall felles stasjon_id og detaljer per fil
    print(f"Antall felles stasjon_id: {len(common_station_ids)}")
    for csv_file, station_ids in station_id_files.items():
        unique_to_file = station_ids - common_station_ids
        print(f"\nFil: {csv_file}")
        print(f"  Totalt antall stasjon_id: {len(station_ids)}")
        print(f"  Antall unike stasjon_id i denne filen: {len(unique_to_file)}")
        print(f"  Antall felles stasjon_id med andre filer: {len(station_ids & common_station_ids)}")

# Eksempel på bruk
csv_folder = r"C:\Users\janaal\Documents\Koding\netatmo"  # Erstatt med banen til mappen som inneholder CSV-filene
csv_files = [os.path.join(csv_folder, file) for file in os.listdir(csv_folder) if file.endswith('.csv')]

compare_station_ids(csv_files)