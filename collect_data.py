import requests
import csv
import os
from datetime import datetime
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()
API_KEY = os.getenv('AVIATIONSTACK_KEY')

# The 3 routes it will be tracking: (departure airport, arrival airport)
ROUTES = [
    ('BOM', 'FRA'),
    ('DEL', 'CDG'),
    ('BLR', 'AMS')
]

CSV_FILE = 'data/flights_log.csv'

def fetch_route_data(dep, arr):
    """Calls the API for one route and returns the flight results."""
    url = 'http://api.aviationstack.com/v1/flights'
    params = {
        'access_key': API_KEY,
        'dep_iata': dep,
        'arr_iata': arr
    }
    response = requests.get(url, params=params)
    return response.json()

def calculate_delay(scheduled, actual):
    """Returns delay in minutes, or None if either time is missing."""
    if not scheduled or not actual:
        return None
    scheduled_dt = datetime.fromisoformat(scheduled)
    actual_dt = datetime.fromisoformat(actual)
    delay = (actual_dt - scheduled_dt).total_seconds() / 60
    return round(delay, 1)

def save_to_csv(flights, dep, arr):
    """Appends each flight found to our CSV file."""
    file_exists = os.path.isfile(CSV_FILE) and os.path.getsize(CSV_FILE) > 0
    
    with open(CSV_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        
        # Write header row only once, when file is first created
        if not file_exists:
            writer.writerow([
                'collected_at', 'route', 'flight_date', 'flight_status',
                'dep_scheduled', 'dep_actual', 'dep_delay_min',
                'arr_scheduled', 'arr_actual', 'arr_delay_min',
                'calculated_dep_delay', 'calculated_arr_delay',
                'flight_number', 'airline'
            ])
        
        for flight in flights.get('data', []):
            writer.writerow([
                datetime.now().isoformat(),
                f'{dep}-{arr}',
                flight.get('flight_date'),
                flight.get('flight_status'),
                flight['departure'].get('scheduled'),
                flight['departure'].get('actual'),
                flight['departure'].get('delay'),
                flight['arrival'].get('scheduled'),
                flight['arrival'].get('actual'),
                flight['arrival'].get('delay'),
                calculate_delay(flight['departure'].get('scheduled'), flight['departure'].get('actual')),
                calculate_delay(flight['arrival'].get('scheduled'), flight['arrival'].get('actual')),
                flight['flight'].get('iata'),
                flight['airline'].get('name')
            ])

def main():
    for dep, arr in ROUTES:
        print(f'Fetching {dep} -> {arr}...')
        data = fetch_route_data(dep, arr)
        save_to_csv(data, dep, arr)
        print(f'  Saved {len(data.get("data", []))} flights.')

if __name__ == '__main__':
    main()