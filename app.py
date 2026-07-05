from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from datetime import datetime
import os
from services.routing_service import calculate_safe_route
from services.crime_scraper import get_latest_headline

app = Flask(__name__, static_folder='static')
CORS(app)

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/sw.js')
def service_worker():
    return send_from_directory(app.static_folder, 'sw.js')

@app.route('/manifest.json')
def manifest():
    return send_from_directory(app.static_folder, 'manifest.json')

@app.route('/api/headline', methods=['GET'])
def fetch_headline():
    location = request.args.get('location')
    if not location:
        return jsonify({"error": "Location is required"}), 400
        
    headline = get_latest_headline(location)
    if headline:
        return jsonify({"headline": headline})
    else:
        return jsonify({"headline": f"Stay vigilant and aware of your surroundings in {location}."})

@app.route('/api/safe-route', methods=['POST'])
def get_safe_route():
    data = request.json
    
    if not data or 'start' not in data or 'destination' not in data:
        return jsonify({"error": "Missing start or destination coordinates"}), 400
        
    start_lat = data['start'].get('lat')
    start_lon = data['start'].get('lon')
    dest_lat = data['destination'].get('lat')
    dest_lon = data['destination'].get('lon')
    travel_time = data.get('time')
    safety_profile = data.get('profile', 'balanced')
    
    if None in [start_lat, start_lon, dest_lat, dest_lon]:
        return jsonify({"error": "Invalid coordinate format"}), 400
        
    try:
        # Calculate routes and crime intersections
        result = calculate_safe_route(
            float(start_lat), 
            float(start_lon), 
            float(dest_lat), 
            float(dest_lon),
            travel_time,
            safety_profile
        )
        
        if "error" in result:
            return jsonify(result), 400
            
        return jsonify(result)
    except ValueError:
        return jsonify({"error": "Coordinates must be numbers"}), 400
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"An internal error occurred: {str(e)}"}), 500

from services.routing_service import get_crime_dataframe
import pandas as pd
from datetime import datetime
import csv
import random

raw_user_reports = []

@app.route('/api/crimes', methods=['GET'])
def get_crimes():
    """Returns a sample of up to 10000 crime points for the heatmap, optionally filtered by time/severity."""
    df = get_crime_dataframe()
    if df is None or df.empty:
        return jsonify({"points": [], "total": 0, "top_crime": "N/A"})
        
    target_time = request.args.get('time')
    
    # Filter by time if provided
    if target_time and 'Time of Occurrence' in df.columns:
        try:
            target_dt = datetime.strptime(target_time, '%H:%M')
            def is_within_window(time_str):
                try:
                    dt = datetime.strptime(time_str.strip(), '%H:%M')
                    diff = abs((dt - target_dt).total_seconds())
                    # Within 2 hours
                    return diff <= 7200 or diff >= (86400 - 7200)
                except:
                    return True
            df = df[df['Time of Occurrence'].apply(is_within_window)]
        except Exception as e:
            pass
            
    total_active = len(df)
    top_crime = "N/A"
    if total_active > 0 and 'Crime Description' in df.columns:
        top_crime = df['Crime Description'].mode()[0]
        
    # Sample up to 10000 points to avoid freezing the browser
    sample_size = min(10000, len(df))
    df_sample = df.sample(n=sample_size) if total_active > 0 else df
    
    # Return as list of [lat, lon, intensity]
    points = [[row['Latitude'], row['Longitude'], 1.0] for _, row in df_sample.iterrows()]
    return jsonify({
        "points": points,
        "total": total_active,
        "top_crime": top_crime
    })

@app.route('/api/report-crime', methods=['POST'])
def report_crime():
    global raw_user_reports
    data = request.json
    
    if not data or 'lat' not in data or 'lon' not in data or 'type' not in data or 'time' not in data:
        return jsonify({"error": "Missing required fields"}), 400
        
    crime_type = data['type']
    
    # Check severity
    high_stakes_crimes = ['Homicide', 'Assault', 'Rape', 'Burglary', 'Kidnapping', 'Murder']
    
    threshold_met = False
    
    if crime_type in high_stakes_crimes:
        # High stakes -> instant validation
        threshold_met = True
    else:
        # Low stakes -> needs 3 reports in the same area (simulated by adding to raw_reports and checking distance)
        raw_user_reports.append(data)
        
        # Check if 3 reports exist within ~1km of each other for the same crime
        nearby_reports = 0
        for report in raw_user_reports:
            if report['type'] == crime_type:
                # very rough distance check
                lat_diff = abs(float(report['lat']) - float(data['lat']))
                lon_diff = abs(float(report['lon']) - float(data['lon']))
                if lat_diff < 0.01 and lon_diff < 0.01:
                    nearby_reports += 1
                    
        if nearby_reports >= 3:
            threshold_met = True
            
    if threshold_met:
        try:
            csv_path = "crime_dataset_final_cleaned_processed.csv"
            df = pd.read_csv(csv_path, engine='python', on_bad_lines='skip', quoting=3)
            
            new_record = {
                'Report Number': f"USER_{random.randint(100000, 999999)}",
                'Date of Occurrence': datetime.now().strftime("%Y-%m-%d"),
                'Time of Occurrence': data['time'],
                'City': "User Reported",
                'Crime Code': 999,
                'Crime Description': crime_type,
                'Victim Age': 30,
                'Victim Gender': 'Unknown',
                'Weapon Used': 'Unknown',
                'Police Deployed': 1,
                'Latitude': float(data['lat']),
                'Longitude': float(data['lon'])
            }
            
            df_new = pd.DataFrame([new_record])
            df_combined = pd.concat([df, df_new], ignore_index=True)
            df_combined.to_csv(csv_path, index=False)
            
            # Reset raw reports for this area/type if it was low stakes
            if crime_type not in high_stakes_crimes:
                raw_user_reports = [r for r in raw_user_reports if not (r['type'] == crime_type and abs(float(r['lat']) - float(data['lat'])) < 0.01)]
                
            return jsonify({"status": "success", "message": "Report verified and added to map."})
        except Exception as e:
            print("Error saving user report:", e)
            return jsonify({"error": "Failed to save report"}), 500
    else:
        return jsonify({"status": "pending", "message": "Report logged. Awaiting further confirmation from other users."})


if __name__ == '__main__':
    from apscheduler.schedulers.background import BackgroundScheduler
    from services.crime_scraper import fetch_latest_crime_news
    
    # Run scraper in the background every 60 minutes
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=fetch_latest_crime_news, trigger="interval", minutes=60)
    scheduler.start()
    
    print("Crime hot-reload and background News scraper active!")
    # Use threaded=True for better performance during development
    app.run(debug=True, threaded=True, host='0.0.0.0', port=5000, use_reloader=False)
