chrome.storage.local.get(["safeRoute", "crimeZones"], function(data) {
    if (!data.safeRoute) return;
    
    let map = document.querySelector("#scene");  // Google Maps canvas
    if (!map) return;

    let safeRouteCoords = data.safeRoute;
    let crimeZones = data.crimeZones;

    function drawPolyline(coords, color) {
        let path = new google.maps.Polyline({
            path: coords.map(c => ({ lat: c[0], lng: c[1] })),
            geodesic: true,
            strokeColor: color,
            strokeOpacity: 1.0,
            strokeWeight: 4
        });
        path.setMap(window.googleMap);
    }

    function drawCrimeZones(zones) {
        zones.forEach(zone => {
            let crimeCircle = new google.maps.Circle({
                center: { lat: zone[0], lng: zone[1] },
                radius: 300,
                strokeColor: "red",
                strokeOpacity: 0.8,
                strokeWeight: 2,
                fillColor: "red",
                fillOpacity: 0.35,
                map: window.googleMap
            });
        });
    }

    drawPolyline(safeRouteCoords, "green");
    drawCrimeZones(crimeZones);
});
