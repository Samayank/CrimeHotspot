import os
import random
import requests
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from geopy.geocoders import Nominatim
import spacy
import time

load_dotenv()

NEWS_API_KEY = os.getenv("NEWS_API_KEY")
DATASET_PATH = "crime_dataset_final_cleaned_processed.csv"

# Base coordinates for jittering if specific geocoding fails
CITY_COORDS = {
    'Delhi': (28.6139, 77.2090),
    'Mumbai': (19.0760, 72.8777)
}

geolocator = Nominatim(user_agent="crime_hotspot_app")

# Load NLP model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Downloading language model for the first time...")
    spacy.cli.download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

def extract_locations(text):
    doc = nlp(text)
    locations = []
    for ent in doc.ents:
        if ent.label_ in ['GPE', 'LOC', 'FAC']:
            locations.append(ent.text)
    return locations

def geocode_exact_location(location_name, city):
    try:
        # Give context to Nominatim
        loc = geolocator.geocode(f"{location_name}, {city}, India")
        if loc:
            return loc.latitude, loc.longitude
        return None, None
    except Exception as e:
        print(f"Geocoding error for {location_name}: {e}")
        return None, None

def fetch_latest_crime_news():
    if not NEWS_API_KEY:
        print("No NEWS_API_KEY found.")
        return False

    url = f"https://newsapi.org/v2/everything?q=(robbery OR murder OR assault OR theft OR snatched OR burglary) AND (Delhi OR Mumbai)&sortBy=publishedAt&language=en&apiKey={NEWS_API_KEY}"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if data.get('status') != 'ok':
            print(f"Error from NewsAPI: {data.get('message')}")
            return False
            
        articles = data.get('articles', [])[:10] # Process top 10 latest
        new_crimes = []
        
        for article in articles:
            title = article['title']
            desc = article['description'] or ""
            text = title + " " + desc
            
            city = "Delhi" if "Delhi" in text else "Mumbai" if "Mumbai" in text else None
            if not city:
                continue
                
            # Use NLP to extract locations
            extracted_locs = extract_locations(text)
            
            lat, lon = None, None
            # Try geocoding extracted locations
            for loc_name in extracted_locs:
                if loc_name.lower() not in ['delhi', 'mumbai', 'india', 'new delhi']:
                    lat, lon = geocode_exact_location(loc_name, city)
                    if lat and lon:
                        print(f"Successfully geocoded extracted landmark: {loc_name}")
                        break
                        
            # Fallback to jitter if NLP geocoding fails
            if lat is None or lon is None:
                base_lat, base_lon = CITY_COORDS[city]
                lat = base_lat + random.uniform(-0.1, 0.1)
                lon = base_lon + random.uniform(-0.1, 0.1)
            
            # Identify crime type
            crime_type = "Other"
            text_lower = text.lower()
            if "robbery" in text_lower or "theft" in text_lower:
                crime_type = "Theft/Robbery"
            elif "murder" in text_lower:
                crime_type = "Homicide"
            elif "assault" in text_lower:
                crime_type = "Assault"
            elif "burglary" in text_lower:
                crime_type = "Burglary"
            
            new_crimes.append({
                'Report Number': f"NEWS_{random.randint(100000, 999999)}",
                'Date of Occurrence': datetime.now().strftime("%Y-%m-%d"),
                'Time of Occurrence': datetime.now().strftime("%H:%M"),
                'City': city,
                'Crime Code': 999,
                'Crime Description': crime_type,
                'Victim Age': 30,
                'Victim Gender': 'Unknown',
                'Weapon Used': 'Unknown',
                'Police Deployed': 1,
                'Latitude': lat,
                'Longitude': lon
            })
            
            time.sleep(1) # Be nice to Nominatim API
            
        if new_crimes:
            df_new = pd.DataFrame(new_crimes)
            df_existing = pd.read_csv(DATASET_PATH, engine='python', on_bad_lines='skip', quoting=3)
            
            df_combined = pd.concat([df_existing, df_new], ignore_index=True)
            df_combined.to_csv(DATASET_PATH, index=False)
            print(f"Scraped and added {len(new_crimes)} real-time crimes from News API.")
            return True
            
    except Exception as e:
        print(f"Failed to scrape news: {e}")
        
        
    return False

def get_latest_headline(location_name):
    """Fetch recent crime headlines specific to a location with date/time stamps."""
    if not NEWS_API_KEY:
        return None
    
    # Crime-specific keywords to ensure relevance
    crime_keywords = ['murder', 'robbery', 'theft', 'assault', 'stabbing', 'shot', 'killed',
                       'arrested', 'snatching', 'burglary', 'rape', 'kidnap', 'attack',
                       'crime', 'police', 'FIR', 'accused', 'victim', 'gang']
    
    query = f'(murder OR robbery OR assault OR theft OR stabbing OR arrested OR kidnap OR snatching OR crime) AND "{location_name}"'
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": query,
        "sortBy": "publishedAt",
        "language": "en",
        "pageSize": 20,
        "apiKey": NEWS_API_KEY
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        if data.get('status') == 'ok' and data.get('articles'):
            headlines = []
            for article in data['articles']:
                title = article.get('title', '')
                if not title or title == '[Removed]':
                    continue
                
                # Filter 1: Must be about the specific location
                title_lower = title.lower()
                desc_lower = (article.get('description', '') or '').lower()
                loc_lower = location_name.lower()
                
                if loc_lower not in title_lower and loc_lower not in desc_lower:
                    continue
                
                # Filter 2: Must contain at least one crime keyword
                if not any(kw in title_lower or kw in desc_lower for kw in crime_keywords):
                    continue
                
                # Format the date
                published = article.get('publishedAt', '')
                date_str = ''
                if published:
                    try:
                        dt = datetime.strptime(published, '%Y-%m-%dT%H:%M:%SZ')
                        date_str = dt.strftime('%d %b, %I:%M %p')
                    except:
                        date_str = published[:10]
                
                source = article.get('source', {}).get('name', '')
                headline = f"[{date_str}] {title}"
                if source:
                    headline += f" — {source}"
                headlines.append(headline)
                
                if len(headlines) >= 5:
                    break
            
            if headlines:
                return " ┃ ".join(headlines)
    except Exception as e:
        print(f"Error fetching headline: {e}")
        
    return None

if __name__ == "__main__":
    fetch_latest_crime_news()
