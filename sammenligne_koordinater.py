import csv
import os
from collections import defaultdict

def parse_and_round_location(location_str):
    # Fjern klammeparenteser og mellomrom, og del opp i breddegrad og lengdegrad
    lat_str, lon_str = location_str.strip()[1:-1].split(',')
    # Konverter til flyttall og rund av til 3 desimaler
    lat = round(float(lat_str), 1)
    lon = round(float(lon_str), 1)
    return lat, lon

def compare_rounded_coordinates(csv_files):
    coordinates_files = defaultdict(set)

    # Les og rund av koordinater fra hver fil, og lagre dem i et sett
    for csv_file in csv_files:
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                location = parse_and_round_location(row['location'])
                coordinates_files[csv_file].add(location)

    # Finn felles koordinater mellom alle filer
    common_coordinates = set.intersection(*coordinates_files.values())

    # Skriv ut antall felles stasjoner basert på avrundede koordinater og detaljer per fil
    print(f"Antall felles stasjoner basert på avrundede koordinater: {len(common_coordinates)}")
    for csv_file, coordinates in coordinates_files.items():
        unique_to_file = coordinates - common_coordinates
        print(f"\nFil: {csv_file}")
        print(f"  Totalt antall stasjoner: {len(coordinates)}")
        print(f"  Antall unike stasjoner i denne filen: {len(unique_to_file)}")
        print(f"  Antall felles stasjoner med andre filer: {len(coordinates & common_coordinates)}")

# Eksempel på bruk
csv_folder = r"C:\Users\janaal\Documents\Koding\netatmo"  # Erstatt med banen til mappen som inneholder CSV-filene
csv_files = [os.path.join(csv_folder, file) for file in os.listdir(csv_folder) if file.endswith('.csv')]

compare_rounded_coordinates(csv_files)
