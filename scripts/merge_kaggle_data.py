import pandas as pd
import numpy as np

def merge_data():
    existing_file = "crime_dataset_final_cleaned_processed.csv"
    kaggle_file = "ride_safety_dataset.csv"
    
    print(f"Loading {existing_file}...")
    df_existing = pd.read_csv(existing_file)
    
    print(f"Loading {kaggle_file}...")
    try:
        df_kaggle = pd.read_csv(kaggle_file, engine='python', on_bad_lines='skip', quoting=3)
    except Exception as e:
        print("Fallback to normal read:", e)
        df_kaggle = pd.read_csv(kaggle_file)
    
    # Filter only Delhi and Mumbai
    df_kaggle = df_kaggle[df_kaggle['City'].isin(['Delhi', 'Mumbai'])]
    
    # Drop rows without coords
    df_kaggle = df_kaggle.dropna(subset=['Latitude', 'Longitude'])
    
    mapped_data = {
        'Report Number': ['K_' + str(i) for i in df_kaggle['Crime_ID']],
        'Date of Occurrence': df_kaggle['Date'],
        'Time of Occurrence': df_kaggle['Time'],
        'City': df_kaggle['City'],
        'Crime Code': [999] * len(df_kaggle),
        'Crime Description': df_kaggle['Crime_Type'],
        'Victim Age': [30] * len(df_kaggle),
        'Victim Gender': df_kaggle['Passenger_Gender'],
        'Weapon Used': ['Unknown'] * len(df_kaggle),
        'Police Deployed': df_kaggle['Num_Police_Stations_Nearby'],
        'Latitude': df_kaggle['Latitude'],
        'Longitude': df_kaggle['Longitude']
    }
    
    df_mapped = pd.DataFrame(mapped_data)
    
    # Concatenate
    df_combined = pd.concat([df_existing, df_mapped], ignore_index=True)
    
    # Save back
    df_combined.to_csv(existing_file, index=False)
    print(f"Merged successfully. Total rows now: {len(df_combined)}")

if __name__ == "__main__":
    merge_data()
