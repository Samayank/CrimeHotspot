// DOM Elements - App Flow
const landingPage = document.getElementById('landing-page');
const loadingScreen = document.getElementById('loading-screen');
const mainApp = document.getElementById('main-app');
const locateMeBtn = document.getElementById('locate-me-btn');
const manualLocationInput = document.getElementById('manual-location-input');
const manualLocationBtn = document.getElementById('manual-location-btn');
const progressBar = document.getElementById('progress-bar');
const loadingSubtext = document.getElementById('loading-subtext');
const newsTicker = document.getElementById('news-ticker');
const tickerText = document.getElementById('ticker-text');

// Mobile Sidebar Toggle
const mobileToggleBtn = document.getElementById('mobile-toggle-btn');
const sidebar = document.getElementById('sidebar');

mobileToggleBtn.addEventListener('click', () => {
    sidebar.classList.toggle('open');
});

// Map Initialization
const map = L.map('map').setView([20.5937, 78.9629], 5); // Default to India center

// Add Dark Matter CartoDB tiles
L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
    subdomains: 'abcd',
    maxZoom: 20
}).addTo(map);

// Layer Groups
let indiaBoundaryLayer = L.layerGroup().addTo(map);
let primaryRouteLayer = L.layerGroup().addTo(map);
let altRouteLayer = L.layerGroup().addTo(map);
let crimeZonesLayer = L.layerGroup().addTo(map);
let crimePointsLayer = L.layerGroup().addTo(map);
let markersLayer = L.layerGroup().addTo(map);
let heatLayer = null;

// DOM Elements
const startInput = document.getElementById('start-input');
const destInput = document.getElementById('dest-input');
const startResults = document.getElementById('start-results');
const destResults = document.getElementById('dest-results');
const timeSlider = document.getElementById('time-slider');
const timeDisplay = document.getElementById('time-display');
const playTimeBtn = document.getElementById('play-time-btn');
const safetyProfile = document.getElementById('safety-profile');
const statTotal = document.getElementById('stat-total');
const statTop = document.getElementById('stat-top');
const findRouteBtn = document.getElementById('find-route-btn');
const statusPanel = document.getElementById('status-panel');
const statusMessage = document.getElementById('status-message');
const loader = document.getElementById('loader');
const legend = document.getElementById('legend');

// Load India State Boundaries (Internal)
fetch('/static/data/india_states_official.geojson')
    .then(response => response.json())
    .then(data => {
        L.geoJSON(data, {
            style: {
                color: '#3b82f6', // Lighter blue for state borders
                weight: 1,
                fillColor: '#1e3a8a',
                fillOpacity: 0.1,
                opacity: 0.5
            }
        }).addTo(indiaBoundaryLayer);
    })
    .catch(err => console.error("Error loading India States GeoJSON:", err));

// Load Full India Country Boundary (Official, includes PoK & Aksai Chin)
fetch('/static/data/india_pok.geojson')
    .then(response => response.json())
    .then(data => {
        L.geoJSON(data, {
            style: {
                color: '#1e3a8a', // Thick dark blue border for the official country outline
                weight: 3,
                fillColor: 'transparent',
                opacity: 1.0
            }
        }).addTo(indiaBoundaryLayer);
    })
    .catch(err => console.error("Error loading India Country GeoJSON:", err));

// State
let startCoords = null;
let destCoords = null;
let debounceTimer;
let userGPSCoords = null; // Stores {lat, lon} from GPS detection
let userLocationMarker = null;
const useMyLocationBtn = document.getElementById('use-my-location-btn');

// Time display helper (must be defined before first use)
function formatTimeDisplay(hourStr) {
    const hour = parseInt(hourStr);
    const suffix = hour >= 12 ? 'PM' : 'AM';
    const displayHour = hour % 12 === 0 ? 12 : hour % 12;
    return `${displayHour}:00 ${suffix}`;
}

// Set default time to current time
const now = new Date();
const currentHourStr = now.toTimeString().slice(0, 2);
timeSlider.value = currentHourStr;
timeDisplay.textContent = formatTimeDisplay(currentHourStr);

// Nominatim Geocoding Function
async function geocodeAddress(query) {
    if (!query) return [];
    try {
        const response = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}&limit=5`);
        return await response.json();
    } catch (error) {
        console.error("Geocoding error:", error);
        return [];
    }
}

// Setup Autocomplete
function setupAutocomplete(inputEl, resultsEl, onSelectCallback) {
    inputEl.addEventListener('input', (e) => {
        clearTimeout(debounceTimer);
        const query = e.target.value;
        
        if (query.length < 3) {
            resultsEl.style.display = 'none';
            return;
        }

        debounceTimer = setTimeout(async () => {
            const results = await geocodeAddress(query);
            resultsEl.innerHTML = '';
            
            if (results.length > 0) {
                results.forEach(place => {
                    const div = document.createElement('div');
                    div.className = 'autocomplete-item';
                    div.textContent = place.display_name;
                    div.addEventListener('click', () => {
                        inputEl.value = place.display_name;
                        resultsEl.style.display = 'none';
                        onSelectCallback({lat: parseFloat(place.lat), lon: parseFloat(place.lon)});
                    });
                    resultsEl.appendChild(div);
                });
                resultsEl.style.display = 'block';
            } else {
                resultsEl.style.display = 'none';
            }
        }, 500);
    });

    // Close autocomplete on outside click
    document.addEventListener('click', (e) => {
        if (e.target !== inputEl && e.target !== resultsEl) {
            resultsEl.style.display = 'none';
        }
    });
}

setupAutocomplete(startInput, startResults, (coords) => { startCoords = coords; });
setupAutocomplete(destInput, destResults, (coords) => { destCoords = coords; });

// Fetch Safe Route
findRouteBtn.addEventListener('click', async () => {
    if (!startCoords || !destCoords) {
        showStatus("Please select both starting and destination points from the dropdown.", "alert-error");
        return;
    }

    clearMap();
    showLoader("Analyzing route for crime hotspots...");

    try {
        const hours = timeSlider.value.padStart(2, '0');
        const formattedTime = `${hours}:00`;

        const response = await fetch('/api/safe-route', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                start: startCoords, 
                destination: destCoords,
                time: formattedTime,
                profile: safetyProfile.value
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Failed to calculate route");
        }

        renderMapData(data);
    } catch (error) {
        showStatus(error.message, "alert-error");
    }
});

function renderMapData(data) {
    statusPanel.classList.remove('hidden');
    loader.classList.add('hidden');
    legend.classList.remove('hidden');

    let bounds = L.latLngBounds();

    // Add Start and End Markers
    const startMarker = L.circleMarker([startCoords.lat, startCoords.lon], {radius: 8, color: '#3b82f6', fillColor: '#3b82f6', fillOpacity: 1}).addTo(markersLayer).bindPopup('Start');
    const destMarker = L.circleMarker([destCoords.lat, destCoords.lon], {radius: 8, color: '#ef4444', fillColor: '#ef4444', fillOpacity: 1}).addTo(markersLayer).bindPopup('Destination');
    bounds.extend(startMarker.getLatLng());
    bounds.extend(destMarker.getLatLng());

    // Draw Crime Zones
    if (data.crime_zones_geojson) {
        L.geoJSON(data.crime_zones_geojson, {
            style: { color: '#ef4444', weight: 1, fillColor: '#ef4444', fillOpacity: 0.3 }
        }).addTo(crimeZonesLayer);
    }

    // Draw Primary Crime Hotspots
    if (data.primary_crimes && data.primary_crimes.length > 0) {
        data.primary_crimes.forEach(crime => {
            const popupContent = `
                <div class="crime-popup">
                    <h4>${crime.description || 'Unknown Crime'}</h4>
                    <p><strong>Date:</strong> ${crime.date || 'N/A'}</p>
                    <p><strong>Time:</strong> ${crime.time || 'N/A'}</p>
                </div>
            `;
            L.circleMarker([crime.lat, crime.lon], {
                radius: 4, color: '#000', weight: 1, fillColor: '#ef4444', fillOpacity: 0.8
            }).addTo(crimePointsLayer).bindPopup(popupContent);
        });
    }

    // Determine status message and routes to draw
    if (data.intersects_crime) {
        // Draw Primary Route in Red/Muted (since it's dangerous)
        L.polyline(data.primary_route, { color: '#6b7280', weight: 4, dashArray: '5, 10' }).addTo(primaryRouteLayer);
        
        if (data.alternative_route && data.alternative_route.length > 0) {
            // Draw Alternative Route in Green
            const altLine = L.polyline(data.alternative_route, { color: '#10b981', weight: 6 }).addTo(altRouteLayer);
            bounds.extend(altLine.getBounds());
            
            showStatus(`<strong>Warning:</strong> Primary route passes through a high-crime area. <br><br> ✅ An alternative safe route has been generated.`, "alert-warning");
            
            // Draw Alternative crimes if any
            if (data.alternative_crimes && data.alternative_crimes.length > 0) {
                 data.alternative_crimes.forEach(crime => {
                    const popupContent = `
                        <div class="crime-popup">
                            <h4>${crime.description || 'Minor Crime'}</h4>
                            <p><strong>Date:</strong> ${crime.date || 'N/A'}</p>
                            <p><strong>Time:</strong> ${crime.time || 'N/A'}</p>
                        </div>
                    `;
                    L.circleMarker([crime.lat, crime.lon], {
                        radius: 4, color: '#000', weight: 1, fillColor: '#f59e0b', fillOpacity: 0.8
                    }).addTo(crimePointsLayer).bindPopup(popupContent);
                });
            }
        } else {
            showStatus(`<strong>Danger:</strong> Primary route passes through a high-crime area, but no viable alternative was found. Proceed with extreme caution.`, "alert-error");
            L.polyline(data.primary_route, { color: '#ef4444', weight: 5 }).addTo(primaryRouteLayer);
            bounds.extend(L.polyline(data.primary_route).getBounds());
        }
    } else {
        // Safe route
        const line = L.polyline(data.primary_route, { color: '#3b82f6', weight: 6 }).addTo(primaryRouteLayer);
        bounds.extend(line.getBounds());
        showStatus(`<strong>Safe Route Found:</strong> Your route does not intersect any known high-crime hotspots.`, "alert-success");
    }

    // Fit map to bounds
    if (bounds.isValid()) {
        map.fitBounds(bounds, { padding: [50, 50] });
    }
    
    // Render Directions
    const directionsPanel = document.getElementById('directions-panel');
    const directionsList = document.getElementById('directions-list');
    
    let activeSteps = data.intersects_crime && data.alternative_route && data.alternative_route.length > 0 
        ? data.alternative_steps 
        : data.primary_steps;
        
    if (activeSteps && activeSteps.length > 0) {
        directionsPanel.classList.remove('hidden');
        directionsList.innerHTML = '';
        activeSteps.forEach(step => {
            const li = document.createElement('li');
            const dist = (step.distance > 1000) ? (step.distance/1000).toFixed(1) + ' km' : step.distance.toFixed(0) + ' m';
            li.innerHTML = `<span>${step.instruction}</span><span class="distance">${dist}</span>`;
            directionsList.appendChild(li);
        });
    } else {
        directionsPanel.classList.add('hidden');
    }
}

function showLoader(message) {
    statusPanel.classList.remove('hidden');
    legend.classList.add('hidden');
    loader.classList.remove('hidden');
    statusMessage.className = '';
    statusMessage.innerHTML = message;
}

function showStatus(message, className) {
    statusPanel.classList.remove('hidden');
    loader.classList.add('hidden');
    statusMessage.className = className;
    statusMessage.innerHTML = message;
}

function clearMap() {
    primaryRouteLayer.clearLayers();
    altRouteLayer.clearLayers();
    crimeZonesLayer.clearLayers();
    crimePointsLayer.clearLayers();
    markersLayer.clearLayers();
}

// User Reporting Logic
let reportLocation = null;

const reportModal = document.getElementById('report-modal');
const closeModalBtn = document.getElementById('close-modal');
const submitReportBtn = document.getElementById('submit-report-btn');
const reportTimeInput = document.getElementById('report-time');
const crimeTypeSelect = document.getElementById('crime-type-select');
const reportStatus = document.getElementById('report-status');

// Set default time in modal
reportTimeInput.value = new Date().toTimeString().slice(0, 5);

map.on('contextmenu', (e) => {
    // Right-click opens the report modal instantly
    openReportModal(e.latlng);
});

function openReportModal(latlng) {
    reportLocation = latlng;
    
    // Reset modal state
    reportStatus.textContent = '';
    reportStatus.className = '';
    submitReportBtn.disabled = false;
    
    reportModal.classList.remove('hidden');
}

closeModalBtn.addEventListener('click', () => {
    reportModal.classList.add('hidden');
    // Exit report mode
    document.getElementById('map').style.cursor = '';
});

submitReportBtn.addEventListener('click', async () => {
    const type = crimeTypeSelect.value;
    const time = reportTimeInput.value;
    
    submitReportBtn.disabled = true;
    reportStatus.textContent = 'Submitting...';
    reportStatus.className = '';
    
    try {
        const response = await fetch('/api/report-crime', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                lat: reportLocation.lat,
                lon: reportLocation.lng,
                type: type,
                time: time
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            reportStatus.textContent = data.message;
            if (data.status === 'success') {
                reportStatus.style.color = '#10b981'; // success green
            } else {
                reportStatus.style.color = '#f59e0b'; // pending warning orange
            }
            
            setTimeout(() => {
                reportModal.classList.add('hidden');
                // Exit report mode
                document.getElementById('map').style.cursor = '';
            }, 3000);
        } else {
            throw new Error(data.error || 'Failed to submit report');
        }
    } catch (err) {
        reportStatus.textContent = err.message;
        reportStatus.style.color = '#ef4444'; // error red
        submitReportBtn.disabled = false;
    }
});

// App Flow Logic

function startLoadingSequence(locationName, userLat, userLon) {
    landingPage.classList.add('hidden');
    loadingScreen.classList.remove('hidden');
    
    // Store user GPS if provided
    if (userLat && userLon) {
        userGPSCoords = { lat: userLat, lon: userLon };
    }
    
    // Animate progress bar
    setTimeout(() => { progressBar.style.width = '30%'; loadingSubtext.textContent = `Connecting to ${locationName} regional databases...`; }, 500);
    setTimeout(() => { progressBar.style.width = '60%'; loadingSubtext.textContent = 'Analyzing recent incidents...'; }, 1500);
    setTimeout(() => { progressBar.style.width = '85%'; loadingSubtext.textContent = 'Generating real-time heatmap...'; }, 2500);
    
    // Fetch headline
    fetch(`/api/headline?location=${encodeURIComponent(locationName)}`)
        .then(res => res.json())
        .then(data => {
            setTimeout(() => {
                progressBar.style.width = '100%';
                loadingSubtext.textContent = 'Complete!';
                
                setTimeout(() => {
                    loadingScreen.classList.add('hidden');
                    mainApp.classList.remove('hidden');
                    
                    if (userLat && userLon) {
                        map.setView([userLat, userLon], 12);
                        
                        // Add user location marker
                        if (userLocationMarker) {
                            map.removeLayer(userLocationMarker);
                        }
                        const userIcon = L.divIcon({
                            html: '<div style="width:16px;height:16px;border-radius:50%;background:#4f46e5;border:3px solid white;box-shadow:0 0 10px rgba(79,70,229,0.8),0 0 30px rgba(79,70,229,0.4);"></div>',
                            className: '',
                            iconSize: [16, 16],
                            iconAnchor: [8, 8]
                        });
                        userLocationMarker = L.marker([userLat, userLon], { icon: userIcon }).addTo(map);
                        userLocationMarker.bindPopup('<strong>📍 You are here</strong>').openPopup();
                    }
                    
                    // Show ticker
                    if (data.headline) {
                        newsTicker.classList.remove('hidden');
                        tickerText.textContent = `🚨 CRIME ALERTS — ${locationName.toUpperCase()} ┃ ${data.headline}`;
                    }
                    
                    // Trigger map resize because it was hidden
                    setTimeout(() => { map.invalidateSize(); }, 200);
                    
                    // Auto-fetch stats on page load
                    fetchStats();
                }, 500);
            }, 1000); // Wait a bit to show 100%
        })
        .catch(err => {
            console.error(err);
            // Fallback
            setTimeout(() => {
                loadingScreen.classList.add('hidden');
                mainApp.classList.remove('hidden');
                setTimeout(() => { map.invalidateSize(); }, 200);
                fetchStats();
            }, 1000);
        });
}

locateMeBtn.addEventListener('click', () => {
    locateMeBtn.textContent = 'Locating...';
    locateMeBtn.disabled = true;
    
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(async (position) => {
            const lat = position.coords.latitude;
            const lon = position.coords.longitude;
            
            try {
                // Reverse geocode to get city/state
                const res = await fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lon}`);
                const data = await res.json();
                
                const city = data.address.city || data.address.state_district || data.address.state || "India";
                
                startLoadingSequence(city, lat, lon);
            } catch (err) {
                console.error(err);
                startLoadingSequence("your area", lat, lon);
            }
        }, (error) => {
            console.error(error);
            alert("Location access denied or failed. Please use manual entry.");
            locateMeBtn.textContent = '📍 Auto-Detect My Location';
            locateMeBtn.disabled = false;
        });
    } else {
        alert("Geolocation is not supported by this browser.");
        locateMeBtn.disabled = false;
    }
});

manualLocationBtn.addEventListener('click', () => {
    const loc = manualLocationInput.value.trim();
    if (loc) {
        // Just use the text input, default India center for now until they search
        startLoadingSequence(loc, 20.5937, 78.9629);
    }
});

// Use My Location button in sidebar
useMyLocationBtn.addEventListener('click', () => {
    if (userGPSCoords) {
        // Already have GPS coords from landing page detection
        startCoords = { lat: userGPSCoords.lat, lon: userGPSCoords.lon };
        startInput.value = '📍 Your Location';
        useMyLocationBtn.textContent = '✅ Location set!';
        useMyLocationBtn.style.color = '#10b981';
        setTimeout(() => {
            useMyLocationBtn.textContent = '📍 Use My Location';
            useMyLocationBtn.style.color = 'var(--accent)';
        }, 2000);
    } else {
        // No cached GPS, try to get it now
        useMyLocationBtn.textContent = '⏳ Detecting...';
        useMyLocationBtn.disabled = true;
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(async (position) => {
                const lat = position.coords.latitude;
                const lon = position.coords.longitude;
                userGPSCoords = { lat, lon };
                startCoords = { lat, lon };
                startInput.value = '📍 Your Location';
                useMyLocationBtn.textContent = '✅ Location set!';
                useMyLocationBtn.style.color = '#10b981';
                useMyLocationBtn.disabled = false;
                
                // Add marker
                if (userLocationMarker) map.removeLayer(userLocationMarker);
                const userIcon = L.divIcon({
                    html: '<div style="width:16px;height:16px;border-radius:50%;background:#4f46e5;border:3px solid white;box-shadow:0 0 10px rgba(79,70,229,0.8),0 0 30px rgba(79,70,229,0.4);"></div>',
                    className: '',
                    iconSize: [16, 16],
                    iconAnchor: [8, 8]
                });
                userLocationMarker = L.marker([lat, lon], { icon: userIcon }).addTo(map);
                userLocationMarker.bindPopup('<strong>📍 You are here</strong>');
                
                setTimeout(() => {
                    useMyLocationBtn.textContent = '📍 Use My Location';
                    useMyLocationBtn.style.color = 'var(--accent)';
                }, 2000);
            }, (err) => {
                useMyLocationBtn.textContent = '❌ Failed';
                useMyLocationBtn.disabled = false;
                setTimeout(() => {
                    useMyLocationBtn.textContent = '📍 Use My Location';
                    useMyLocationBtn.style.color = 'var(--accent)';
                }, 2000);
            });
        }
    }
});

// Time Slider Logic
let playInterval = null;

timeSlider.addEventListener('input', (e) => {
    timeDisplay.textContent = formatTimeDisplay(e.target.value);
    if (isHeatmapActive) {
        updateHeatmap();
    }
});

playTimeBtn.addEventListener('click', () => {
    if (playInterval) {
        clearInterval(playInterval);
        playInterval = null;
        playTimeBtn.textContent = '▶ Play';
        playTimeBtn.style.color = 'var(--accent)';
    } else {
        playTimeBtn.textContent = '⏸ Pause';
        playTimeBtn.style.color = 'var(--danger)';
        playInterval = setInterval(() => {
            let nextVal = parseInt(timeSlider.value) + 1;
            if (nextVal > 23) nextVal = 0;
            timeSlider.value = nextVal;
            timeDisplay.textContent = formatTimeDisplay(nextVal);
            if (isHeatmapActive) {
                updateHeatmap();
            }
        }, 1500); // Change time every 1.5s
    }
});

// Stats fetcher (used on page load and by heatmap)
async function fetchStats() {
    try {
        const hours = timeSlider.value.padStart(2, '0');
        const formattedTime = `${hours}:00`;
        const res = await fetch(`/api/crimes?time=${formattedTime}`);
        const data = await res.json();
        statTotal.textContent = data.total || 0;
        statTop.textContent = data.top_crime || 'N/A';
    } catch (err) {
        console.error('Failed to fetch stats', err);
    }
}

// Heatmap Logic
let isHeatmapActive = false;
const heatmapBtn = document.getElementById('toggle-heatmap-btn');

async function updateHeatmap() {
    try {
        const hours = timeSlider.value.padStart(2, '0');
        const formattedTime = `${hours}:00`;
        const res = await fetch(`/api/crimes?time=${formattedTime}`);
        const data = await res.json();
        
        statTotal.textContent = data.total || 0;
        statTop.textContent = data.top_crime || 'N/A';
        
        if (heatLayer) {
            map.removeLayer(heatLayer);
        }
        
        heatLayer = L.heatLayer(data.points, {
            radius: 12,
            blur: 15,
            maxZoom: 11,
            max: 1.0,
            gradient: {0.4: 'blue', 0.6: 'cyan', 0.7: 'lime', 0.8: 'yellow', 1.0: 'red'}
        }).addTo(map);
    } catch (err) {
        console.error("Failed to load heatmap", err);
    }
}

heatmapBtn.addEventListener('click', async () => {
    isHeatmapActive = !isHeatmapActive;
    
    if (isHeatmapActive) {
        heatmapBtn.innerHTML = '🔥 Hide Crime Heatmap';
        heatmapBtn.classList.add('active');
        await updateHeatmap();
    } else {
        if (heatLayer) {
            map.removeLayer(heatLayer);
        }
        statTotal.textContent = '0';
        statTop.textContent = 'N/A';
        heatmapBtn.innerHTML = '🔥 Toggle Crime Heatmap';
        heatmapBtn.classList.remove('active');
    }
});

// Add PWA Service Worker Registration
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js')
            .then(reg => console.log('Service Worker registered!', reg))
            .catch(err => console.error('Service Worker registration failed: ', err));
    });
}
