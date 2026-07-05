let map;
let directionsService;
let directionsRenderer;

// Dynamically load Google Maps API
function loadGoogleMaps() {
    if (!document.getElementById("googleMaps")) {
        let script = document.createElement("script");
        script.id = "googleMaps";
        script.src = "https://maps.googleapis.com/maps/api/js?key=AIzaSyCCzlW7IfXbg8DBBTMimiCn50WjwfOELrA&callback=initMap";
        script.async = true;
        script.defer = true;
        document.head.appendChild(script);
    }
}

// Load Google Maps when popup opens
document.addEventListener("DOMContentLoaded", loadGoogleMaps);



// Initialize Google Maps when API is ready
function initMap() {
    map = new google.maps.Map(document.getElementById("map"), {
        center: { lat: 40.7128, lng: -74.0060 }, // Default: New York
        zoom: 12,
    });

    directionsService = new google.maps.DirectionsService();
    directionsRenderer = new google.maps.DirectionsRenderer();
    directionsRenderer.setMap(map);
}

// Load Google Maps when popup opens
document.addEventListener("DOMContentLoaded", () => {
    loadGoogleMaps();
});
