import pandas as pd
import numpy as np
import random
from geopy.geocoders import Nominatim
from datetime import datetime, timedelta
import time
import os

# Initialize Nominatim geocoder
geolocator = Nominatim(user_agent="crime_hotspot_app")

INPUT_FILE = "../NCRB_Table_1A.1.csv"
OUTPUT_FILE = "../crime_dataset_final_cleaned_processed.csv"

# Pre-defined crime types and weapons to make it look realistic
CRIME_TYPES = ["Theft/Robbery", "Assault", "Burglary", "Homicide", "Kidnapping", "Drug Offense"]
WEAPONS = ["Unknown", "Blunt Object", "Knife", "Firearm", "None"]

def generate_random_date(start_year=2022, end_year=2023):
    start_date = datetime(start_year, 1, 1)
    end_date = datetime(end_year, 12, 31)
    delta = end_date - start_date
    random_days = random.randrange(delta.days)
    return start_date + timedelta(days=random_days)

def geocode_state(state_name):
    # Try to geocode with "India" appended for better accuracy
    try:
        location = geolocator.geocode(f"{state_name}, India")
        if location:
            return location.latitude, location.longitude
        return None, None
    except Exception as e:
        print(f"Error geocoding {state_name}: {e}")
        return None, None

def generate_dataset():
    # Use absolute paths or correct relative paths. Assuming script runs from root or scripts dir.
    current_dir = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.join(current_dir, "..", "NCRB_Table_1A.1.csv")
    output_path = os.path.join(current_dir, "..", "crime_dataset_final_cleaned_processed.csv")

    if not os.path.exists(input_path):
        print(f"Error: {input_path} not found.")
        return

    print("Loading NCRB dataset...")
    try:
        df_ncrb = pd.read_csv(input_path)
    except Exception as e:
        print(f"Failed to read CSV: {e}")
        return
        
    print(f"Initial columns: {df_ncrb.columns}")

    # Remove the total rows
    df_ncrb = df_ncrb[~df_ncrb['State/UT'].astype(str).str.contains('Total', na=False, case=False)]
    
    # We want State/UT and 2022
    df_ncrb['2022'] = pd.to_numeric(df_ncrb['2022'], errors='coerce')
    df_ncrb = df_ncrb.dropna(subset=['2022'])

    generated_crimes = []
    report_counter = 1

    print("Generating proportional points for each State/UT (1 point per 100 crimes)...")
    for index, row in df_ncrb.iterrows():
        state = row['State/UT'].strip()
        crimes_2022 = int(row['2022'])
        
        # Scale down points (1 per 100)
        points_to_generate = max(1, crimes_2022 // 100)
        
        print(f"Geocoding {state}... (Will generate {points_to_generate} points)")
        lat, lon = geocode_state(state)
        
        if lat is None or lon is None:
            print(f"Warning: Could not geocode {state}. Skipping.")
            continue
            
        time.sleep(1) # Be nice to Nominatim API
        
        # Generate points
        for _ in range(points_to_generate):
            # Jitter roughly up to ~22km (much tighter bound for city-level density)
            jitter_lat = lat + random.uniform(-0.2, 0.2)
            jitter_lon = lon + random.uniform(-0.2, 0.2)
            
            occ_date = generate_random_date()
            
            crime_record = {
                'Report Number': f"NCRB_{report_counter}",
                'Date of Occurrence': occ_date.strftime("%Y-%m-%d"),
                'Time of Occurrence': f"{random.randint(0, 23):02d}:{random.randint(0, 59):02d}",
                'City': state,
                'Crime Code': random.randint(100, 999),
                'Crime Description': random.choice(CRIME_TYPES),
                'Victim Age': random.randint(18, 65),
                'Victim Gender': random.choice(['M', 'F', 'Unknown']),
                'Weapon Used': random.choice(WEAPONS),
                'Police Deployed': random.randint(0, 10),
                'Latitude': jitter_lat,
                'Longitude': jitter_lon
            }
            
            generated_crimes.append(crime_record)
            report_counter += 1

    if not generated_crimes:
        print("No crimes generated.")
        return

    df_final = pd.DataFrame(generated_crimes)
    df_final.to_csv(output_path, index=False)
    print(f"Successfully generated {len(df_final)} crime points and saved to {output_path}.")

if __name__ == "__main__":
    generate_dataset()
