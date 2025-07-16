import os
import requests
import csv
from datetime import datetime

API_KEY = os.getenv('OWM_API_KEY')  # paims raktą iš GitHub Secrets
BASE_URL = 'https://api.openweathermap.org/data/2.5/weather'
UNITS = 'metric'

LOCATIONS = [
    {'name': 'K2 Base Camp', 'lat': 35.83455, 'lon': 76.50927, 'elev': 4965},
    {'name': 'K2 Summit',    'lat': 35.88250, 'lon': 76.51333, 'elev': 8611},
]

def fetch_weather(lat, lon):
    params = {'lat': lat, 'lon': lon, 'appid': API_KEY, 'units': UNITS}
    resp = requests.get(BASE_URL, params=params)
    resp.raise_for_status()
    return resp.json()

def parse_data(data, loc):
    dt = datetime.utcfromtimestamp(data['dt']).strftime('%Y-%m-%d %H:%M:%S')
    main   = data.get('main', {})
    wind   = data.get('wind', {})
    clouds = data.get('clouds', {})
    weather= data.get('weather', [{}])[0]
    rain   = data.get('rain', {}).get('1h', 0)
    snow   = data.get('snow', {}).get('1h', 0)

    return [
        loc['name'], dt, loc['lat'], loc['lon'],
        main.get('temp',''), main.get('feels_like',''),
        main.get('temp_min',''), main.get('temp_max',''),
        main.get('pressure',''), main.get('humidity',''),
        wind.get('speed',''), wind.get('deg',''),
        clouds.get('all',''),
        weather.get('main',''), weather.get('description',''),
        rain, snow, loc['elev']
    ]

def write_csv(rows, filename='weather.csv'):
    header = [
        'location','datetime','lat','lon',
        'temp','feels_like','temp_min','temp_max',
        'pressure','humidity',
        'wind_speed','wind_deg',
        'clouds','weather_main','weather_desc',
        'rain_1h','snow_1h','elevation_m'
    ]
    try:
        with open(filename, 'r', encoding='utf-8'):
            exists = True
    except FileNotFoundError:
        exists = False

    with open(filename, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not exists:
            writer.writerow(header)
        writer.writerows(rows)

if __name__ == '__main__':
    all_rows = []
    for loc in LOCATIONS:
        data = fetch_weather(loc['lat'], loc['lon'])
        row  = parse_data(data, loc)
        all_rows.append(row)
    write_csv(all_rows)
