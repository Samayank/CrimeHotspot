# Krimehotpot
crime hotspot detection using geofencing and geospatial anyalsis

Overview

Crime Hotspot Detection is a web application that identifies crime-prone areas and provides an alternate safer route to users. The system leverages Folium for interactive mapping and OpenRouteService API for route optimization while avoiding high-crime areas.

Features

Crime Hotspot Visualization: Displays crime-prone areas on a map using Folium.

Crime Risk Level Prediction: Uses a neural network model to analyze crime data and predict risk levels.

Alternate Safer Route Suggestion: Provides a safer route option avoiding crime hotspots using OpenRouteService.

Google Maps Integration: Displays routes and hotspots in a Chrome extension.

Real-Time Data Processing: Processes large datasets (~40K+ crime entries across India).

Tech Stack

Backend: Python, Flask

Frontend: JavaScript, HTML, CSS, Google Maps API

Database: PostgreSQL / SQLite (optional)

Machine Learning: TensorFlow / PyTorch for neural network-based predictions

Mapping API: Folium, OpenRouteService API, Google Maps API

Installation

Prerequisites

Python 3.8+

Node.js (for Chrome extension)

PostgreSQL (if using a database)

API keys for Google Maps API and OpenRouteService API

Steps

Clone the repository

git clone https://github.com/yourusername/crime-hotspot-detection.git
cd crime-hotspot-detection

Set up a virtual environment

python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

Install dependencies

pip install -r requirements.txt

Set up environment variables (create a .env file)

GOOGLE_MAPS_API_KEY=your_google_maps_api_key
OPENROUTESERVICE_API_KEY=your_openrouteservice_api_key

Run the application

python app.py

Install Chrome Extension (Optional)

Open chrome://extensions/

Enable Developer Mode

Click Load Unpacked and select the chrome_extension folder

Usage

Open the web application and enter a location to check crime hotspots.

Use the "Find Safer Route" button to get a crime-free alternate route.

Chrome extension automatically overlays crime hotspots on Google Maps.

Route Calculation Logic

Load Crime Data: Reads crime data from a CSV file containing latitude and longitude.

Generate Crime Zones: Clusters high-crime areas and creates polygons using Shapely.

Get Routes: Fetches routes from OpenRouteService API while avoiding high-crime zones.

Validate Safer Routes: Checks if the primary route intersects a crime zone and suggests an alternative route if necessary.

Display on Map: Uses Folium to visualize the routes and crime zones.

API Endpoints

/predict – Predicts crime risk for a given location.

/hotspots – Returns geo-coordinates of high-crime areas.

/safe-route – Returns an optimized safer route avoiding crime hotspots.

Contributing

Fork the repo

Create a new branch (git checkout -b feature-branch)

Commit changes (git commit -m 'Add feature')

Push to GitHub (git push origin feature-branch)

Open a pull request

