# Crime Hotspot Detection

CrimeHotspot is an advanced web application and Progressive Web App (PWA) designed to enhance pedestrian and commuter safety. It identifies crime-prone areas in real-time and provides optimized, safer travel routes. The system leverages Leaflet.js for interactive dynamic mapping, OpenRouteService API for navigation, and a robust Flask backend for geospatial processing.

## 🚀 Key Features

*   **Interactive Dynamic Mapping:** Replaced static maps with a responsive **Leaflet.js** frontend interface, providing smooth panning, zooming, and dynamic layers.
*   **Intelligent Route Planning:** Calculates routes avoiding high-crime zones using OpenRouteService. Users can select **Safety Profiles** (Balanced, Safest, Fastest) and specify the **Time of Travel** to get context-aware safe routes.
*   **Live Crime Heatmap:** Toggleable heatmap showing historical and recent crime data, temporally filtered to match your travel time.
*   **Crowdsourced Crime Reporting:** Right-click anywhere on the map to report live incidents. Features a smart validation system (instant validation for high-stakes crimes like Assault/Homicide, and multi-report thresholds for minor incidents).
*   **Live Local News Ticker:** A background scheduler scrapes the latest localized crime news and alerts, displaying them dynamically on the map interface.
*   **Statistics Dashboard:** Real-time on-map overlay displaying total active incidents and top crime categories for the selected region.
*   **PWA Support:** Installable as a Progressive Web App with offline capabilities and a native app-like experience on mobile devices.
*   **Chrome Extension (Optional):** Integration to overlay crime hotspots directly onto Google Maps via the included extension.

## 🛠️ Tech Stack

**Frontend:**
*   HTML5, CSS3 (Modern Glassmorphism UI), JavaScript (ES6+)
*   **Leaflet.js** & Leaflet.heat for map rendering and heatmaps
*   Service Workers & Web App Manifest for PWA Support

**Backend & Data Processing:**
*   **Python, Flask**: RESTful API and web server framework
*   **Pandas, Shapely**: Geospatial data manipulation and zone buffering
*   **APScheduler**: Background jobs for live news scraping
*   **Spacy, Geopy**: NLP and Geocoding services

**APIs:**
*   **OpenRouteService API**: For routing and navigation
*   **News Scraping**: Custom background services fetching headlines

## ⚙️ Installation and Setup

### Prerequisites
*   Python 3.8+
*   Node.js (optional, for extension development)
*   API keys for OpenRouteService

### Steps

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/yourusername/crime-hotspot-detection.git
    cd crime-hotspot-detection
    ```

2.  **Set up a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use: venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables:**
    Create a `.env` file in the root directory and add your API keys:
    ```env
    OPENROUTESERVICE_API_KEY=your_openrouteservice_api_key
    ```

5.  **Run the application:**
    ```bash
    python app.py
    ```
    *The app will be available at `http://localhost:5000`.*

6.  **Install Chrome Extension (Optional):**
    *   Open `chrome://extensions/`
    *   Enable **Developer Mode**
    *   Click **Load Unpacked** and select the `crime_map_extension` folder.

## 📖 Usage

1.  **Launch the App**: Open the web application. You'll be greeted by a landing page to auto-detect your location or manually enter a city.
2.  **Find a Safe Route**: Enter your Start and Destination points, select your Travel Time via the slider, choose a Safety Profile, and hit **Find Safe Route**. The map will display the Primary Route and an Alternative Safe Route if necessary.
3.  **Toggle Heatmap**: Use the sidebar button to visualize crime density.
4.  **Report an Incident**: Right-click on any map location to open the Report Modal. Submit crime details to alert other users.
5.  **Stay Informed**: Watch the scrolling news ticker for the latest local safety updates.

## 📡 Core API Endpoints

*   `GET /api/crimes?time=HH:MM` - Fetches sample crime data points for the heatmap, filtered by the specified time window.
*   `POST /api/safe-route` - Calculates the safest route between start and destination coordinates based on the selected safety profile.
*   `GET /api/headline?location=City` - Retrieves the latest scraped crime news headline for the user's location.
*   `POST /api/report-crime` - Accepts crowdsourced crime reports, with threshold checks for low-stakes crimes.

## 🤝 Contributing

1.  Fork the repo
2.  Create a new branch (`git checkout -b feature-branch`)
3.  Commit your changes (`git commit -m 'Add feature'`)
4.  Push to the branch (`git push origin feature-branch`)
5.  Open a Pull Request

---
*Developed to make everyday navigation safer and smarter.*
