import os
import openrouteservice
import pandas as pd
from shapely.geometry import Point, LineString, mapping, MultiPoint
from shapely.ops import unary_union
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

API_KEY = os.getenv("OPENROUTESERVICE_API_KEY")

# Load crime dataset with hot-reloading
FILE_PATH = "crime_dataset_final_cleaned_processed.csv"
last_mtime = 0
df = None

def get_crime_dataframe():
    global df, last_mtime
    try:
        current_mtime = os.path.getmtime(FILE_PATH)
        if current_mtime > last_mtime or df is None:
            df = pd.read_csv(FILE_PATH, engine='python', on_bad_lines='skip', quoting=3)
            df = df[['Latitude', 'Longitude', 'Crime Description', 'Date of Occurrence', 'Time of Occurrence']].dropna()
            last_mtime = current_mtime
    except Exception as e:
        print(f"Error loading dataset: {e}")
    return df

def get_route(start, dest, avoid_polygons=None):
    """Get route between two points, avoiding crime zones if specified."""
    if not API_KEY:
        raise ValueError("OpenRouteService API Key is missing in .env")

    client = openrouteservice.Client(key=API_KEY)
    
    try:
        params = {
            "coordinates": [[start[1], start[0]], [dest[1], dest[0]]],  # ORS uses [lon, lat]
            "profile": "driving-car",
            "format": "geojson",
            "radiuses": [2000, 2000], # Increase snapping radius to 2km to prevent 404 errors
            "validate": True
        }
        if avoid_polygons:
            params["options"] = {"avoid_polygons": mapping(avoid_polygons)}

        return client.directions(**params)
    except Exception as e:
        print(f"Error calculating route: {e}")
        return None

def filter_crimes_along_route(route_coords, buffer_distance=200, travel_time=None):
    """Find crimes that occurred within `buffer_distance` of the route and within a 3-hour window."""
    crime_data = get_crime_dataframe()
    if crime_data is None or crime_data.empty:
        return []
    
    route_line = LineString(route_coords)
    nearby_crimes = []
    
    # Parse user travel time if provided
    travel_dt = None
    if travel_time:
        try:
            travel_dt = datetime.strptime(travel_time, "%H:%M")
        except ValueError:
            pass

    for _, row in crime_data.iterrows():
        crime_point = Point(float(row["Longitude"]), float(row["Latitude"]))
        # Approximate distance in meters (1 degree ~ 111,000 meters)
        distance = route_line.distance(crime_point) * 111000
        
        if distance <= buffer_distance:
            # Check time proximity
            time_str = str(row["Time of Occurrence"])
            if travel_dt and time_str and time_str != 'nan':
                try:
                    crime_dt = datetime.strptime(time_str, "%H:%M")
                    # Calculate difference in hours, accounting for midnight wrap-around
                    diff = abs((travel_dt - crime_dt).total_seconds()) / 3600.0
                    if diff > 12:
                        diff = 24 - diff
                        
                    # Skip if difference is more than 3 hours
                    if diff > 3:
                        continue
                except ValueError:
                    pass
                    
            nearby_crimes.append({
                "lat": float(row["Latitude"]),
                "lon": float(row["Longitude"]),
                "description": str(row["Crime Description"]),
                "date": str(row["Date of Occurrence"]),
                "time": str(row["Time of Occurrence"])
            })

    return nearby_crimes

import functools

def create_crime_zones(crime_hotspots, buffer_size=0.002):
    """Create high-crime area polygons from filtered crime data."""
    if not crime_hotspots:
        return None
        
    crime_buffers = [Point(float(c["lon"]), float(c["lat"])).buffer(buffer_size) for c in crime_hotspots]
    
    if not crime_buffers:
        return None
        
    # Using reduce completely bypasses the Shapely 2.0 numpy ufunc coercion bugs
    return functools.reduce(lambda a, b: a.union(b), crime_buffers)

def is_route_in_crime_zone(route_coords, crime_polygon):
    """Check if a route intersects with a high-crime zone."""
    if not crime_polygon:
        return False
    route_line = LineString(route_coords)
    return route_line.intersects(crime_polygon)

def calculate_safe_route(start_lat, start_lon, dest_lat, dest_lon, travel_time=None, safety_profile='balanced'):
    """
    Main logic to calculate a primary route and an alternative safe route if needed.
    Returns a dictionary of coordinates and features for the frontend.
    """
    start = (start_lat, start_lon)
    destination = (dest_lat, dest_lon)

    primary_route = get_route(start, destination)
    
    if not primary_route:
        return {"error": "No route found. Check coordinates or API key."}

    # Extract primary route coordinates as [lon, lat]
    route_coords = [(coord[0], coord[1]) for coord in primary_route['features'][0]['geometry']['coordinates']]
    
    # Determine buffer distance based on safety profile
    buffer_dist = 500
    if safety_profile == 'safest':
        buffer_dist = 1000
    elif safety_profile == 'fastest':
        buffer_dist = 200

    # Filter crime hotspots for primary route
    crime_hotspots_primary = filter_crimes_along_route(route_coords, buffer_distance=buffer_dist, travel_time=travel_time)
    crime_zones = create_crime_zones(crime_hotspots_primary)

    alternative_route = None
    crime_hotspots_alt = []
    intersects_crime = False

    if crime_zones and is_route_in_crime_zone(route_coords, crime_zones):
        intersects_crime = True
        
        # Get alternative route avoiding crime zones
        alternative_route = get_route(start, destination, avoid_polygons=crime_zones)
        
        if alternative_route:
            alt_route_coords = [(coord[0], coord[1]) for coord in alternative_route['features'][0]['geometry']['coordinates']]
            crime_hotspots_alt = filter_crimes_along_route(alt_route_coords, buffer_distance=500, travel_time=travel_time)

    # Format output for frontend mapping (Leaflet expects [lat, lon])
    def format_coords_for_leaflet(geojson_route):
        if not geojson_route:
            return []
        return [[c[1], c[0]] for c in geojson_route['features'][0]['geometry']['coordinates']]

    # Prepare polygons for leaflet
    zones_geojson = mapping(crime_zones) if crime_zones else None
    
    primary_steps = primary_route['features'][0].get('properties', {}).get('segments', [{}])[0].get('steps', []) if primary_route else []
    alternative_steps = alternative_route['features'][0].get('properties', {}).get('segments', [{}])[0].get('steps', []) if alternative_route else []

    return {
        "status": "success",
        "primary_route": format_coords_for_leaflet(primary_route),
        "alternative_route": format_coords_for_leaflet(alternative_route),
        "primary_crimes": crime_hotspots_primary, # [lat, lon]
        "alternative_crimes": crime_hotspots_alt, # [lat, lon]
        "intersects_crime": intersects_crime,
        "crime_zones_geojson": zones_geojson,
        "primary_steps": primary_steps,
        "alternative_steps": alternative_steps
    }
