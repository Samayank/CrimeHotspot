# import folium
# from folium.plugins import MarkerCluster
# import openrouteservice
# import pandas as pd
# from shapely.geometry import Point, Polygon, LineString, MultiPolygon, mapping
# from shapely.ops import unary_union

# # Load crime dataset
# file_path = "crime_dataset_final_cleaned_processed.csv"
# df = pd.read_csv(file_path)
# df = df[['Latitude', 'Longitude']].dropna()

# def get_route(start, dest, api_key, avoid_polygons=None):
#     """Get route between two points, avoiding crime zones if specified."""
#     client = openrouteservice.Client(key=api_key)

#     try:
#         params = {
#             "coordinates": [start, dest],
#             "profile": "driving-car",
#             "format": "geojson",
#             "validate": True
#         }
#         if avoid_polygons:
#             params["options"] = {"avoid_polygons": mapping(avoid_polygons)}

#         return client.directions(**params)
#     except Exception as e:
#         print(f"❌ Error calculating route: {e}")
#         return None

# def create_crime_zones(crime_data, buffer_size=0.002):
#     """Create high-crime area polygons using crime data clustering."""
#     crime_points = [Point(lon, lat) for lat, lon in zip(crime_data["Latitude"], crime_data["Longitude"])]
#     if not crime_points:
#         return None

#     crime_buffers = [p.buffer(buffer_size) for p in crime_points]
#     return unary_union(crime_buffers)  # Merge overlapping zones

# def is_route_in_crime_zone(route_coords, crime_polygon):
#     """Check if a route intersects with a high-crime zone."""
#     route_line = LineString(route_coords)
#     return route_line.intersects(crime_polygon)

# def display_map(start, dest, route, alt_route, crime_data, crime_zones):
#     """Display the map with primary and alternative routes."""
#     center = [(start[1] + dest[1]) / 2, (start[0] + dest[0]) / 2]
#     crime_map = folium.Map(location=center, zoom_start=14)

#     # Add start & destination markers
#     folium.Marker(location=[start[1], start[0]], popup="Start", icon=folium.Icon(color="green")).add_to(crime_map)
#     folium.Marker(location=[dest[1], dest[0]], popup="Destination", icon=folium.Icon(color="red")).add_to(crime_map)

#     # Extract primary route coordinates
#     route_coords = [(coord[1], coord[0]) for coord in route['features'][0]['geometry']['coordinates']]
    
#     # Add primary route to map
#     folium.PolyLine(route_coords, color="blue", weight=5, opacity=0.8, popup="Primary Route").add_to(crime_map)

#     # If alternative route exists, add it
#     if alt_route:
#         alt_coords = [(coord[1], coord[0]) for coord in alt_route['features'][0]['geometry']['coordinates']]
#         folium.PolyLine(alt_coords, color="green", weight=5, opacity=0.8, popup="Alternative Route").add_to(crime_map)
#         print("✅ Alternative safer route found and displayed!")
#     else:
#         print("⚠ No alternative route found. Proceed with caution.")

#     # Add crime hotspot markers
#     marker_cluster = MarkerCluster().add_to(crime_map)
#     for _, row in crime_data.iterrows():
#         folium.CircleMarker(
#             location=[row["Latitude"], row["Longitude"]],
#             radius=3,
#             color="darkred",
#             fill=True,
#             popup="Crime Incident"
#         ).add_to(marker_cluster)

#     # Add crime zones to map
#     if crime_zones:
#         if isinstance(crime_zones, MultiPolygon):  # If multiple crime polygons exist
#             for polygon in crime_zones.geoms:
#                 folium.Polygon(
#                     locations=[(lat, lon) for lon, lat in polygon.exterior.coords],
#                     color="red",
#                     fill=True,
#                     fill_opacity=0.3,
#                     popup="High Crime Zone"
#                 ).add_to(crime_map)
#         else:  # Single crime polygon
#             folium.Polygon(
#                 locations=[(lat, lon) for lon, lat in crime_zones.exterior.coords],
#                 color="red",
#                 fill=True,
#                 fill_opacity=0.3,
#                 popup="High Crime Zone"
#             ).add_to(crime_map)

#     # Save map
#     crime_map.save("crime_route_with_alternative.html")
#     print("✅ Map saved as crime_route_with_alternative.html")

# def main():
#     """Main execution function."""
#     api_key = "5b3ce3597851110001cf62487728600986d14f3a8c4bce2711134303"  # Replace with your API key

#     try:
#         # Get user input
#         start_lat = float(input("Enter start latitude: "))
#         start_lon = float(input("Enter start longitude: "))
#         dest_lat = float(input("Enter destination latitude: "))
#         dest_lon = float(input("Enter destination longitude: "))

#         start_coords = (start_lon, start_lat)
#         dest_coords = (dest_lon, dest_lat)

#         # Generate crime zones
#         crime_zones = create_crime_zones(df)

#         # Get primary route
#         primary_route = get_route(start_coords, dest_coords, api_key)

#         if not primary_route:
#             print("❌ No route found. Check coordinates or API key.")
#             return

#         # Extract primary route coordinates
#         route_coords = [(coord[0], coord[1]) for coord in primary_route['features'][0]['geometry']['coordinates']]

#         # Check if primary route intersects high-crime zones
#         if crime_zones and is_route_in_crime_zone(route_coords, crime_zones):
#             print("⚠ WARNING: Your route passes through a high-crime area!")

#             # Try finding an alternative route avoiding crime zones
#             alternative_route = get_route(start_coords, dest_coords, api_key, avoid_polygons=crime_zones)

#             if alternative_route:
#                 print("✅ Alternative safer route found!")
#             else:
#                 print("⚠ No alternative route available. Proceed with caution.")
#         else:
#             print("✅ Primary route is safe.")
#             alternative_route = None

#         # Display final map
#         display_map(start_coords, dest_coords, primary_route, alternative_route, df, crime_zones)

#     except ValueError:
#         print("❌ Error: Please enter valid coordinates")
#     except Exception as e:
#         print(f"❌ An error occurred: {str(e)}")

# if __name__ == "__main__":
#     main()








# import folium
# from folium.plugins import MarkerCluster
# import openrouteservice
# import pandas as pd
# from shapely.geometry import Point, Polygon, LineString, MultiPolygon, mapping
# from shapely.ops import unary_union

# # Load crime dataset
# file_path = "crime_dataset_final_cleaned_processed.csv"
# df = pd.read_csv(file_path)
# df = df[['Latitude', 'Longitude']].dropna()

# def get_route(start, dest, api_key, avoid_polygons=None):
#     """Get route between two points, avoiding crime zones if specified."""
#     client = openrouteservice.Client(key=api_key)

#     try:
#         params = {
#             "coordinates": [start, dest],
#             "profile": "driving-car",
#             "format": "geojson",
#             "validate": True
#         }
#         if avoid_polygons:
#             params["options"] = {"avoid_polygons": mapping(avoid_polygons)}

#         return client.directions(**params)
#     except Exception as e:
#         print(f"❌ Error calculating route: {e}")
#         return None

# def create_crime_zones(crime_data, buffer_size=0.002):
#     """Create high-crime area polygons using crime data clustering."""
#     crime_points = [Point(lon, lat) for lat, lon in zip(crime_data["Latitude"], crime_data["Longitude"])]
#     if not crime_points:
#         return None

#     crime_buffers = [p.buffer(buffer_size) for p in crime_points]
#     return unary_union(crime_buffers)  # Merge overlapping zones

# def is_route_in_crime_zone(route_coords, crime_polygon):
#     """Check if a route intersects with a high-crime zone."""
#     route_line = LineString(route_coords)
#     return route_line.intersects(crime_polygon)

# def display_map(start, dest, route, alt_route, crime_data, crime_zones):
#     """Display the map with primary and alternative routes."""
#     center = [(start[1] + dest[1]) / 2, (start[0] + dest[0]) / 2]
#     crime_map = folium.Map(location=center, zoom_start=14)

#     # Add start & destination markers
#     folium.Marker(location=[start[1], start[0]], popup="Start", icon=folium.Icon(color="green")).add_to(crime_map)
#     folium.Marker(location=[dest[1], dest[0]], popup="Destination", icon=folium.Icon(color="red")).add_to(crime_map)

#     # Extract primary route coordinates
#     route_coords = [(coord[1], coord[0]) for coord in route['features'][0]['geometry']['coordinates']]
    
#     # Add primary route to map
#     folium.PolyLine(route_coords, color="blue", weight=5, opacity=0.8, popup="Primary Route").add_to(crime_map)

#     # If alternative route exists, add it
#     if alt_route:
#         alt_coords = [(coord[1], coord[0]) for coord in alt_route['features'][0]['geometry']['coordinates']]
#         folium.PolyLine(alt_coords, color="green", weight=5, opacity=0.8, popup="Alternative Route").add_to(crime_map)
#         print("✅ Alternative safer route found and displayed!")
#     else:
#         print("⚠ No alternative route found. Proceed with caution.")

#     # Add crime hotspot markers
#     marker_cluster = MarkerCluster().add_to(crime_map)
#     for _, row in crime_data.iterrows():
#         folium.CircleMarker(
#             location=[row["Latitude"], row["Longitude"]],
#             radius=0.125,  # Increased size
#             color="black",
#             fill=True,
#             fill_color="red",  # Makes it stand out
#             fill_opacity=0.8,
#             popup="Crime Hotspot"
#         ).add_to(marker_cluster)

#     # Add crime zones to map
#     if crime_zones:
#         if isinstance(crime_zones, MultiPolygon):  # If multiple crime polygons exist
#             for polygon in crime_zones.geoms:
#                 folium.Polygon(
#                     locations=[(lat, lon) for lon, lat in polygon.exterior.coords],
#                     color="red",
#                     fill=True,
#                     fill_color="darkred",
#                     fill_opacity=0.4,  # Increased visibility
#                     popup="High Crime Zone"
#                 ).add_to(crime_map)
#         else:  # Single crime polygon
#             folium.Polygon(
#                 locations=[(lat, lon) for lon, lat in crime_zones.exterior.coords],
#                 color="red",
#                 fill=True,
#                 fill_color="darkred",
#                 fill_opacity=0.4,
#                 popup="High Crime Zone"
#             ).add_to(crime_map)

#     # Save map
#     crime_map.save("crime_route_with_alternative.html")
#     print("✅ Map saved as crime_route_with_alternative.html")

# def main():
#     """Main execution function."""
#     api_key = "5b3ce3597851110001cf62487728600986d14f3a8c4bce2711134303"  # Replace with your API key

#     try:
#         # Get user input
#         start_lat = float(input("Enter start latitude: "))
#         start_lon = float(input("Enter start longitude: "))
#         dest_lat = float(input("Enter destination latitude: "))
#         dest_lon = float(input("Enter destination longitude: "))

#         start_coords = (start_lon, start_lat)
#         dest_coords = (dest_lon, dest_lat)

#         # Generate crime zones
#         crime_zones = create_crime_zones(df)

#         # Get primary route
#         primary_route = get_route(start_coords, dest_coords, api_key)

#         if not primary_route:
#             print("❌ No route found. Check coordinates or API key.")
#             return

#         # Extract primary route coordinates
#         route_coords = [(coord[0], coord[1]) for coord in primary_route['features'][0]['geometry']['coordinates']]

#         # Check if primary route intersects high-crime zones
#         if crime_zones and is_route_in_crime_zone(route_coords, crime_zones):
#             print("⚠ WARNING: Your route passes through a high-crime area!")

#             # Try finding an alternative route avoiding crime zones
#             alternative_route = get_route(start_coords, dest_coords, api_key, avoid_polygons=crime_zones)

#             if alternative_route:
#                 print("✅ Alternative safer route found!")
#             else:
#                 print("⚠ No alternative route available. Proceed with caution.")
#         else:
#             print("✅ Primary route is safe.")
#             alternative_route = None

#         # Display final map
#         display_map(start_coords, dest_coords, primary_route, alternative_route, df, crime_zones)

#     except ValueError:
#         print("❌ Error: Please enter valid coordinates")
#     except Exception as e:
#         print(f"❌ An error occurred: {str(e)}")

# if __name__ == "__main__":
#     main()








# import folium
# from folium.plugins import MarkerCluster
# import openrouteservice
# import pandas as pd
# from shapely.geometry import Point, Polygon, LineString, MultiPolygon, mapping
# from shapely.ops import unary_union
# from geopy.distance import geodesic
# import geocoder

# # Load crime dataset
# file_path = "crime_dataset_final_cleaned_processed.csv"
# df = pd.read_csv(file_path)
# df = df[['Latitude', 'Longitude']].dropna()

# API_KEY = "5b3ce3597851110001cf62487728600986d14f3a8c4bce2711134303"  # Replace with your key

# def get_live_location():
#     """Get live location using geocoder (latitude, longitude)."""
#     try:
#         g = geocoder.ip('me')  # Gets location from public IP
#         if g.latlng:
#             return g.latlng
#         else:
#             print("❌ Could not fetch live location. Enter manually.")
#             lat = float(input("Enter your current latitude: "))
#             lon = float(input("Enter your current longitude: "))
#             return (lat, lon)
#     except Exception as e:
#         print(f"❌ Error getting live location: {e}")
#         return None

# def filter_nearby_crime_hotspots(crime_data, location, radius=200):
#     """Filter crime hotspots within a given radius (meters) of a location."""
#     nearby_crimes = []
#     for _, row in crime_data.iterrows():
#         crime_point = (row["Latitude"], row["Longitude"])
#         distance = geodesic(location, crime_point).meters  # Calculate distance in meters
#         if distance <= radius:
#             nearby_crimes.append((row["Latitude"], row["Longitude"]))
#     return nearby_crimes

# def get_route(start, dest, avoid_polygons=None):
#     """Get route between two points, avoiding crime zones if specified."""
#     client = openrouteservice.Client(key=API_KEY)

#     try:
#         params = {
#             "coordinates": [(start[1], start[0]), (dest[1], dest[0])],  # (lon, lat) format
#             "profile": "driving-car",
#             "format": "geojson",
#             "validate": True
#         }
#         if avoid_polygons:
#             params["options"] = {"avoid_polygons": mapping(avoid_polygons)}

#         return client.directions(**params)
#     except Exception as e:
#         print(f"❌ Error calculating route: {e}")
#         return None

# def create_crime_zones(crime_hotspots, buffer_size=0.002):
#     """Create high-crime area polygons from filtered crime data."""
#     crime_points = [Point(lon, lat) for lat, lon in crime_hotspots]
#     if not crime_points:
#         return None

#     crime_buffers = [p.buffer(buffer_size) for p in crime_points]
#     return unary_union(crime_buffers)  # Merge overlapping zones

# def is_route_in_crime_zone(route_coords, crime_polygon):
#     """Check if a route intersects with a high-crime zone."""
#     route_line = LineString(route_coords)
#     return route_line.intersects(crime_polygon)

# def display_map(start, dest, route, alt_route, crime_hotspots, crime_zones):
#     """Display the map with the main route, alternative route, and crime hotspots."""
#     center = [(start[0] + dest[0]) / 2, (start[1] + dest[1]) / 2]
#     crime_map = folium.Map(location=center, zoom_start=14)

#     # Add start & destination markers
#     folium.Marker(location=start, popup="Your Location", icon=folium.Icon(color="blue")).add_to(crime_map)
#     folium.Marker(location=dest, popup="Destination", icon=folium.Icon(color="red")).add_to(crime_map)

#     # Extract primary route coordinates
#     if route:
#         route_coords = [(coord[1], coord[0]) for coord in route['features'][0]['geometry']['coordinates']]
#         folium.PolyLine(route_coords, color="blue", weight=5, opacity=0.8, popup="Primary Route").add_to(crime_map)

#     # If alternative route exists, add it
#     if alt_route:
#         alt_coords = [(coord[1], coord[0]) for coord in alt_route['features'][0]['geometry']['coordinates']]
#         folium.PolyLine(alt_coords, color="green", weight=5, opacity=0.8, popup="Alternative Route").add_to(crime_map)
#         print("✅ Alternative safer route found and displayed!")
#     else:
#         print("⚠ No alternative route found. Proceed with caution.")

#     # Add crime hotspot markers
#     marker_cluster = MarkerCluster().add_to(crime_map)
#     for crime in crime_hotspots:
#         folium.CircleMarker(
#             location=crime,
#             radius=5,
#             color="black",
#             fill=True,
#             fill_color="red",
#             fill_opacity=0.8,
#             popup="Crime Hotspot"
#         ).add_to(marker_cluster)

#     # Add crime zones to map
#     if crime_zones:
#         if isinstance(crime_zones, MultiPolygon):  # If multiple crime polygons exist
#             for polygon in crime_zones.geoms:
#                 folium.Polygon(
#                     locations=[(lat, lon) for lon, lat in polygon.exterior.coords],
#                     color="red",
#                     fill=True,
#                     fill_color="darkred",
#                     fill_opacity=0.4,
#                     popup="High Crime Zone"
#                 ).add_to(crime_map)
#         else:  # Single crime polygon
#             folium.Polygon(
#                 locations=[(lat, lon) for lon, lat in crime_zones.exterior.coords],
#                 color="red",
#                 fill=True,
#                 fill_color="darkred",
#                 fill_opacity=0.4,
#                 popup="High Crime Zone"
#             ).add_to(crime_map)

#     # Save map
#     crime_map.save("crime_route_with_alternative.html")
#     print("✅ Map saved as crime_route_with_alternative.html")

# def main():
#     """Main execution function."""
#     try:
#         # Get live location
#         live_location = get_live_location()
#         if not live_location:
#             return

#         # Get user input for destination
#         dest_lat = float(input("Enter destination latitude: "))
#         dest_lon = float(input("Enter destination longitude: "))
#         destination = (dest_lat, dest_lon)

#         # Filter crime hotspots within 1 km radius of live location
#         nearby_crimes = filter_nearby_crime_hotspots(df, live_location, 1000)

#         if not nearby_crimes:
#             print("✅ No crime hotspots found within 1 km of your location.")
#         else:
#             print(f"⚠ Found {len(nearby_crimes)} crime hotspots nearby!")

#         # Generate crime zones from nearby crime hotspots
#         crime_zones = create_crime_zones(nearby_crimes)

#         # Get primary route
#         primary_route = get_route(live_location, destination)

#         if not primary_route:
#             print("❌ No route found. Check coordinates or API key.")
#             return

#         # Extract primary route coordinates
#         route_coords = [(coord[0], coord[1]) for coord in primary_route['features'][0]['geometry']['coordinates']]

#         # Check if primary route intersects high-crime zones
#         if crime_zones and is_route_in_crime_zone(route_coords, crime_zones):
#             print("⚠ WARNING: Your route passes through a high-crime area!")

#             # Try finding an alternative route avoiding crime zones
#             alternative_route = get_route(live_location, destination, avoid_polygons=crime_zones)

#             if alternative_route:
#                 print("✅ Alternative safer route found!")
#             else:
#                 print("⚠ No alternative route available. Proceed with caution.")
#         else:
#             print("✅ Primary route is safe.")
#             alternative_route = None

#         # Display final map
#         display_map(live_location, destination, primary_route, alternative_route, nearby_crimes, crime_zones)

#     except ValueError:
#         print("❌ Error: Please enter valid coordinates")
#     except Exception as e:
#         print(f"❌ An error occurred: {str(e)}")

# if __name__ == "__main__":
#     main()






# import folium
# from folium.plugins import MarkerCluster
# import openrouteservice
# import pandas as pd
# from shapely.geometry import Point, Polygon, LineString, MultiPolygon, mapping
# from shapely.ops import unary_union
# from geopy.distance import geodesic

# # Load crime dataset
# file_path = "crime_dataset_final_cleaned_processed.csv"
# df = pd.read_csv(file_path)
# df = df[['Latitude', 'Longitude']].dropna()

# API_KEY = "5b3ce3597851110001cf62487728600986d14f3a8c4bce2711134303"  # Replace with your key

# def filter_crimes_along_route(crime_data, route_coords, buffer_distance=500):
#     """Filter crime hotspots within a given buffer distance (meters) along the route."""
#     route_line = LineString(route_coords)
#     nearby_crimes = []
    
#     for _, row in crime_data.iterrows():
#         crime_point = Point(row["Longitude"], row["Latitude"])
#         distance = route_line.distance(crime_point) * 111000  # Convert degrees to meters
#         if distance <= buffer_distance:
#             nearby_crimes.append((row["Latitude"], row["Longitude"]))
    
#     return nearby_crimes

# def get_route(start, dest, avoid_polygons=None):
#     """Get route between two points, avoiding crime zones if specified."""
#     client = openrouteservice.Client(key=API_KEY)

#     try:
#         params = {
#             "coordinates": [(start[1], start[0]), (dest[1], dest[0])],  # (lon, lat) format
#             "profile": "driving-car",
#             "format": "geojson",
#             "validate": True
#         }
#         if avoid_polygons:
#             params["options"] = {"avoid_polygons": mapping(avoid_polygons)}

#         return client.directions(**params)
#     except Exception as e:
#         print(f"❌ Error calculating route: {e}")
#         return None

# def create_crime_zones(crime_hotspots, buffer_size=0.002):
#     """Create high-crime area polygons from filtered crime data."""
#     crime_points = [Point(lon, lat) for lat, lon in crime_hotspots]
#     if not crime_points:
#         return None

#     crime_buffers = [p.buffer(buffer_size) for p in crime_points]
#     return unary_union(crime_buffers)  # Merge overlapping zones

# def is_route_in_crime_zone(route_coords, crime_polygon):
#     """Check if a route intersects with a high-crime zone."""
#     route_line = LineString(route_coords)
#     return route_line.intersects(crime_polygon)

# def display_map(start, dest, route, alt_route, crime_hotspots, crime_zones):
#     """Display the map with the main route, alternative route, and crime hotspots."""
#     center = [(start[0] + dest[0]) / 2, (start[1] + dest[1]) / 2]
#     crime_map = folium.Map(location=center, zoom_start=14)

#     # Add start & destination markers
#     folium.Marker(location=start, popup="Source Location", icon=folium.Icon(color="blue")).add_to(crime_map)
#     folium.Marker(location=dest, popup="Destination", icon=folium.Icon(color="red")).add_to(crime_map)

#     # Extract primary route coordinates
#     if route:
#         route_coords = [(coord[1], coord[0]) for coord in route['features'][0]['geometry']['coordinates']]
#         folium.PolyLine(route_coords, color="blue", weight=5, opacity=0.8, popup="Primary Route").add_to(crime_map)

#     # If alternative route exists, add it
#     if alt_route:
#         alt_coords = [(coord[1], coord[0]) for coord in alt_route['features'][0]['geometry']['coordinates']]
#         folium.PolyLine(alt_coords, color="green", weight=5, opacity=0.8, popup="Alternative Route").add_to(crime_map)
#         print("✅ Alternative safer route found and displayed!")
#     else:
#         print("⚠ No alternative route found. Proceed with caution.")

#     # Add crime hotspot markers
#     marker_cluster = MarkerCluster().add_to(crime_map)
#     for crime in crime_hotspots:
#         folium.CircleMarker(
#             location=crime,
#             radius=5,
#             color="black",
#             fill=True,
#             fill_color="red",
#             fill_opacity=0.8,
#             popup="Crime Hotspot"
#         ).add_to(marker_cluster)

#     # Add crime zones to map
#     if crime_zones:
#         if isinstance(crime_zones, MultiPolygon):  # If multiple crime polygons exist
#             for polygon in crime_zones.geoms:
#                 folium.Polygon(
#                     locations=[(lat, lon) for lon, lat in polygon.exterior.coords],
#                     color="red",
#                     fill=True,
#                     fill_color="darkred",
#                     fill_opacity=0.4,
#                     popup="High Crime Zone"
#                 ).add_to(crime_map)
#         else:  # Single crime polygon
#             folium.Polygon(
#                 locations=[(lat, lon) for lon, lat in crime_zones.exterior.coords],
#                 color="red",
#                 fill=True,
#                 fill_color="darkred",
#                 fill_opacity=0.4,
#                 popup="High Crime Zone"
#             ).add_to(crime_map)

#     # Save map
#     crime_map.save("crime_route_with_alternative.html")
#     print("✅ Map saved as crime_route_with_alternative.html")

# def main():
#     """Main execution function."""
#     try:
#         # Get user input for source and destination
#         source_lat = float(input("Enter source latitude: "))
#         source_lon = float(input("Enter source longitude: "))
#         destination_lat = float(input("Enter destination latitude: "))
#         destination_lon = float(input("Enter destination longitude: "))

#         source = (source_lat, source_lon)
#         destination = (destination_lat, destination_lon)

#         # Get primary route
#         primary_route = get_route(source, destination)

#         if not primary_route:
#             print("❌ No route found. Check coordinates or API key.")
#             return

#         # Extract primary route coordinates
#         route_coords = [(coord[0], coord[1]) for coord in primary_route['features'][0]['geometry']['coordinates']]

#         # Filter crime hotspots within the route corridor
#         route_crimes = filter_crimes_along_route(df, route_coords, buffer_distance=500)

#         if not route_crimes:
#             print("✅ No crime hotspots found along the route.")
#         else:
#             print(f"⚠ Found {len(route_crimes)} crime hotspots along the route!")

#         # Generate crime zones from filtered crime hotspots
#         crime_zones = create_crime_zones(route_crimes)

#         # Check if primary route intersects high-crime zones
#         if crime_zones and is_route_in_crime_zone(route_coords, crime_zones):
#             print("⚠ WARNING: Your route passes through a high-crime area!")

#             # Try finding an alternative route avoiding crime zones
#             alternative_route = get_route(source, destination, avoid_polygons=crime_zones)

#             if alternative_route:
#                 print("✅ Alternative safer route found!")
#             else:
#                 print("⚠ No alternative route available. Proceed with caution.")
#         else:
#             print("✅ Primary route is safe.")
#             alternative_route = None

#         # Display final map
#         display_map(source, destination, primary_route, alternative_route, route_crimes, crime_zones)

#     except ValueError:
#         print("❌ Error: Please enter valid coordinates")
#     except Exception as e:
#         print(f"❌ An error occurred: {str(e)}")

# if __name__ == "__main__":
#     main()








# import folium
# from folium.plugins import MarkerCluster
# import openrouteservice
# import pandas as pd
# from shapely.geometry import Point, Polygon, LineString, MultiPolygon, mapping
# from shapely.ops import unary_union
# from geopy.distance import geodesic

# # Load crime dataset
# file_path = "crime_dataset_final_cleaned_processed.csv"
# df = pd.read_csv(file_path)
# df = df[['Latitude', 'Longitude']].dropna()

# API_KEY = "5b3ce3597851110001cf62487728600986d14f3a8c4bce2711134303"  # Replace with your key

# def filter_crimes_along_route(crime_data, route_coords, buffer_distance=500):
#     """Filter crime hotspots within a given buffer distance (meters) along the route."""
#     route_line = LineString(route_coords)
#     return [
#         (row["Latitude"], row["Longitude"])
#         for _, row in crime_data.iterrows()
#         if route_line.distance(Point(row["Longitude"], row["Latitude"])) * 111000 <= buffer_distance
#     ]

# def get_route(start, dest, avoid_polygons=None):
#     """Get route between two points, avoiding crime zones if specified."""
#     client = openrouteservice.Client(key=API_KEY)
#     try:
#         params = {
#             "coordinates": [(start[1], start[0]), (dest[1], dest[0])],
#             "profile": "driving-car",
#             "format": "geojson",
#             "validate": True,
#             "alternative_routes": {"target_count": 3, "share_factor": 0.7}  # Get multiple routes
#         }
#         if avoid_polygons:
#             params["options"] = {"avoid_polygons": mapping(avoid_polygons)}
#         return client.directions(**params)
#     except Exception as e:
#         print(f"❌ Error calculating route: {e}")
#         return None

# def create_crime_zones(crime_hotspots, buffer_size=0.002):
#     """Create high-crime area polygons from filtered crime data."""
#     crime_points = [Point(lon, lat) for lat, lon in crime_hotspots]
#     return unary_union([p.buffer(buffer_size) for p in crime_points]) if crime_points else None

# def is_route_in_crime_zone(route_coords, crime_polygon):
#     """Check if a route intersects with a high-crime zone."""
#     return LineString(route_coords).intersects(crime_polygon)

# def count_crimes_on_route(route_coords, crime_hotspots):
#     """Count the number of crime hotspots along a given route."""
#     route_line = LineString(route_coords)
#     return sum(
#         1 for lat, lon in crime_hotspots if route_line.distance(Point(lon, lat)) * 111000 <= 500
#     )

# def find_safest_route(routes, crime_hotspots):
#     """Find the safest route with the least crime hotspots."""
#     route_crime_counts = [
#         (route, count_crimes_on_route([(c[0], c[1]) for c in route['features'][0]['geometry']['coordinates']], crime_hotspots))
#         for route in routes
#     ]
#     return min(route_crime_counts, key=lambda x: x[1], default=(None, None))[0]

# def display_map(start, dest, primary_route, alternative_route, safest_route, crime_hotspots, crime_zones):
#     """Display the map with all routes and crime data."""
#     center = [(start[0] + dest[0]) / 2, (start[1] + dest[1]) / 2]
#     crime_map = folium.Map(location=center, zoom_start=14)

#     folium.Marker(start, popup="Source", icon=folium.Icon(color="blue")).add_to(crime_map)
#     folium.Marker(dest, popup="Destination", icon=folium.Icon(color="red")).add_to(crime_map)

#     if primary_route:
#         route_coords = [(c[1], c[0]) for c in primary_route['features'][0]['geometry']['coordinates']]
#         folium.PolyLine(route_coords, color="blue", weight=5, popup="Primary Route").add_to(crime_map)

#     if alternative_route:
#         alt_coords = [(c[1], c[0]) for c in alternative_route['features'][0]['geometry']['coordinates']]
#         folium.PolyLine(alt_coords, color="green", weight=5, popup="Alternative Route").add_to(crime_map)

#     if safest_route:
#         safe_coords = [(c[1], c[0]) for c in safest_route['features'][0]['geometry']['coordinates']]
#         folium.PolyLine(safe_coords, color="yellow", weight=5, popup="Safest Route").add_to(crime_map)

#     marker_cluster = MarkerCluster().add_to(crime_map)
#     for crime in crime_hotspots:
#         folium.CircleMarker(crime, radius=5, color="black", fill=True, fill_color="red", fill_opacity=0.8).add_to(marker_cluster)

#     if crime_zones:
#         for polygon in crime_zones.geoms if isinstance(crime_zones, MultiPolygon) else [crime_zones]:
#             folium.Polygon(
#                 locations=[(lat, lon) for lon, lat in polygon.exterior.coords],
#                 color="red", fill=True, fill_color="darkred", fill_opacity=0.4
#             ).add_to(crime_map)

#     crime_map.save("crime_route_with_alternative.html")
#     print("✅ Map saved as crime_route_with_alternative.html")

# def main():
#     """Main execution function."""
#     try:
#         source = (float(input("Enter source latitude: ")), float(input("Enter source longitude: ")))
#         destination = (float(input("Enter destination latitude: ")), float(input("Enter destination longitude: ")))

#         # Get multiple routes
#         routes = get_route(source, destination)
#         if not routes:
#             print("❌ No route found.")
#             return

#         # Extract primary and alternative routes
#         primary_route = routes['routes'][0] if routes['routes'] else None
#         alternative_routes = routes['routes'][1:] if len(routes['routes']) > 1 else []

#         # Extract primary route coordinates
#         primary_coords = [(c[0], c[1]) for c in primary_route['features'][0]['geometry']['coordinates']]

#         # Find crime hotspots along the primary route
#         route_crimes = filter_crimes_along_route(df, primary_coords)

#         if not route_crimes:
#             print("✅ No crime hotspots found along the primary route.")
#             safest_route = None
#         else:
#             print(f"⚠ Found {len(route_crimes)} crime hotspots along the route!")

#             # Generate crime zones
#             crime_zones = create_crime_zones(route_crimes)

#             # Find the safest route from alternatives
#             safest_route = find_safest_route(alternative_routes, route_crimes)

#             if safest_route:
#                 print("✅ A safer route has been found and highlighted in yellow!")
#             else:
#                 print("⚠ No safer route found. Proceed with caution.")

#         # Display map
#         display_map(source, destination, primary_route, alternative_routes[0] if alternative_routes else None, safest_route, route_crimes, crime_zones)

#     except ValueError:
#         print("❌ Error: Please enter valid coordinates")
#     except Exception as e:
#         print(f"❌ An error occurred: {str(e)}")

# if __name__ == "__main__":
#     main()









# import folium
# from folium.plugins import MarkerCluster
# import openrouteservice
# import pandas as pd
# from shapely.geometry import Point, Polygon, LineString, MultiPolygon, mapping
# from shapely.ops import unary_union
# from geopy.distance import geodesic

# # Load crime dataset
# file_path = "crime_dataset_final_cleaned_processed.csv"
# df = pd.read_csv(file_path)
# df = df[['Latitude', 'Longitude']].dropna()

# API_KEY = "5b3ce3597851110001cf62487728600986d14f3a8c4bce2711134303"  # Replace with your key

# def filter_crimes_along_route(crime_data, route_coords, buffer_distance=300):
#     """Filter crime hotspots within a given buffer distance (meters) along the route."""
#     route_line = LineString(route_coords)
#     nearby_crimes = []
    
#     for _, row in crime_data.iterrows():
#         crime_point = Point(row["Longitude"], row["Latitude"])
#         distance = route_line.distance(crime_point) * 111000  # Convert degrees to meters
#         if distance <= buffer_distance:
#             nearby_crimes.append((row["Latitude"], row["Longitude"]))
    
#     return nearby_crimes

# def get_route(start, dest, avoid_polygons=None):
#     """Get route between two points, avoiding crime zones if specified."""
#     client = openrouteservice.Client(key=API_KEY)

#     try:
#         params = {
#             "coordinates": [(start[1], start[0]), (dest[1], dest[0])],  # (lon, lat) format
#             "profile": "driving-car",
#             "format": "geojson",
#             "validate": True
#         }
#         if avoid_polygons:
#             params["options"] = {"avoid_polygons": mapping(avoid_polygons)}

#         return client.directions(**params)
#     except Exception as e:
#         print(f"❌ Error calculating route: {e}")
#         return None

# def create_crime_zones(crime_hotspots, buffer_size=0.002):
#     """Create high-crime area polygons from filtered crime data."""
#     crime_points = [Point(lon, lat) for lat, lon in crime_hotspots]
#     if not crime_points:
#         return None

#     crime_buffers = [p.buffer(buffer_size) for p in crime_points]
#     return unary_union(crime_buffers)  # Merge overlapping zones

# def is_route_in_crime_zone(route_coords, crime_polygon):
#     """Check if a route intersects with a high-crime zone."""
#     route_line = LineString(route_coords)
#     return route_line.intersects(crime_polygon)

# def display_map(start, dest, route, alt_route, crime_hotspots, crime_zones):
#     """Display the map with the main route, alternative route, and crime hotspots."""
#     center = [(start[0] + dest[0]) / 2, (start[1] + dest[1]) / 2]
#     crime_map = folium.Map(location=center, zoom_start=14)

#     # Add start & destination markers
#     folium.Marker(location=start, popup="Source Location", icon=folium.Icon(color="blue")).add_to(crime_map)
#     folium.Marker(location=dest, popup="Destination", icon=folium.Icon(color="red")).add_to(crime_map)

#     # Extract primary route coordinates
#     if route:
#         route_coords = [(coord[1], coord[0]) for coord in route['features'][0]['geometry']['coordinates']]
#         folium.PolyLine(route_coords, color="blue", weight=5, opacity=0.8, popup="Primary Route").add_to(crime_map)

#     # If alternative route exists, add it
#     if alt_route:
#         alt_coords = [(coord[1], coord[0]) for coord in alt_route['features'][0]['geometry']['coordinates']]
#         folium.PolyLine(alt_coords, color="green", weight=5, opacity=0.8, popup="Alternative Route").add_to(crime_map)
#         print("✅ Alternative safer route found and displayed!")
#     else:
#         print("⚠ No alternative route found. Proceed with caution.")

#     # Add crime hotspot markers
#     marker_cluster = MarkerCluster().add_to(crime_map)
#     for crime in crime_hotspots:
#         folium.CircleMarker(
#             location=crime,
#             radius=5,
#             color="black",
#             fill=True,
#             fill_color="red",
#             fill_opacity=0.8,
#             popup="Crime Hotspot"
#         ).add_to(marker_cluster)

#     # Add crime zones to map
#     if crime_zones:
#         if isinstance(crime_zones, MultiPolygon):  # If multiple crime polygons exist
#             for polygon in crime_zones.geoms:
#                 folium.Polygon(
#                     locations=[(lat, lon) for lon, lat in polygon.exterior.coords],
#                     color="red",
#                     fill=True,
#                     fill_color="darkred",
#                     fill_opacity=0.4,
#                     popup="High Crime Zone"
#                 ).add_to(crime_map)
#         else:  # Single crime polygon
#             folium.Polygon(
#                 locations=[(lat, lon) for lon, lat in crime_zones.exterior.coords],
#                 color="red",
#                 fill=True,
#                 fill_color="darkred",
#                 fill_opacity=0.4,
#                 popup="High Crime Zone"
#             ).add_to(crime_map)

#     # Save map
#     crime_map.save("crime_route_with_alternative.html")
#     print("✅ Map saved as crime_route_with_alternative.html")

# def main():
#     """Main execution function."""
#     try:
#         # Get user input for source and destination
#         source_lat = float(input("Enter source latitude: "))
#         source_lon = float(input("Enter source longitude: "))
#         destination_lat = float(input("Enter destination latitude: "))
#         destination_lon = float(input("Enter destination longitude: "))

#         source = (source_lat, source_lon)
#         destination = (destination_lat, destination_lon)

#         # Get primary route
#         primary_route = get_route(source, destination)

#         if not primary_route:
#             print("❌ No route found. Check coordinates or API key.")
#             return

#         # Extract primary route coordinates
#         route_coords = [(coord[0], coord[1]) for coord in primary_route['features'][0]['geometry']['coordinates']]

#         # Filter crime hotspots within the route corridor
#         route_crimes = filter_crimes_along_route(df, route_coords, buffer_distance=500)

#         if not route_crimes:
#             print("✅ No crime hotspots found along the route.")
#         else:
#             print(f"⚠ Found {len(route_crimes)} crime hotspots along the route!")

#         # Generate crime zones from filtered crime hotspots
#         crime_zones = create_crime_zones(route_crimes)

#         # Check if primary route intersects high-crime zones
#         if crime_zones and is_route_in_crime_zone(route_coords, crime_zones):
#             print("⚠ WARNING: Your route passes through a high-crime area!")

#             # Try finding an alternative route avoiding crime zones
#             alternative_route = get_route(source, destination, avoid_polygons=crime_zones)

#             if alternative_route:
#                 print("✅ Alternative safer route found!")
#             else:
#                 print("⚠ No alternative route available. Proceed with caution.")
#         else:
#             print("✅ Primary route is safe.")
#             alternative_route = None

#         # Display final map
#         display_map(source, destination, primary_route, alternative_route, route_crimes, crime_zones)

#     except ValueError:
#         print("❌ Error: Please enter valid coordinates")
#     except Exception as e:
#         print(f"❌ An error occurred: {str(e)}")

# if __name__ == "__main__":
#     main()














import folium
from folium.plugins import MarkerCluster
import openrouteservice
import pandas as pd
from shapely.geometry import Point, Polygon, LineString, MultiPolygon, mapping
from shapely.ops import unary_union

# Load crime dataset
file_path = "crime_dataset_final_cleaned_processed.csv"
df = pd.read_csv(file_path)
df = df[['Latitude', 'Longitude']].dropna()

API_KEY = "5b3ce3597851110001cf62487728600986d14f3a8c4bce2711134303"  # Replace with your key

def filter_crimes_along_route(crime_data, route_coords, buffer_distance=300, severity_filter="all"):
    """Filter crimes along a route based on severity level."""
    route_line = LineString(route_coords)
    nearby_crimes = []

    for _, row in crime_data.iterrows():
        crime_point = Point(row["Longitude"], row["Latitude"])
        distance = route_line.distance(crime_point) * 111000  # Convert degrees to meters

        if distance <= buffer_distance:
            severity = row.get("Severity", "Medium")  # Default to Medium if no severity column

            if severity_filter == "high" and severity == "High":
                nearby_crimes.append((row["Latitude"], row["Longitude"]))
            elif severity_filter == "medium" and severity in ["Medium", "High"]:
                nearby_crimes.append((row["Latitude"], row["Longitude"]))
            elif severity_filter == "all":
                nearby_crimes.append((row["Latitude"], row["Longitude"]))

    return nearby_crimes

def get_route(start, dest, avoid_polygons=None):
    """Get route between two points, avoiding crime zones if specified."""
    client = openrouteservice.Client(key=API_KEY)

    try:
        params = {
            "coordinates": [(start[1], start[0]), (dest[1], dest[0])],  # (lon, lat) format
            "profile": "driving-car",
            "format": "geojson",
            "validate": True
        }
        if avoid_polygons:
            params["options"] = {"avoid_polygons": mapping(avoid_polygons)}

        return client.directions(**params)
    except Exception as e:
        print(f"❌ Error calculating route: {e}")
        return None

def create_crime_zones(crime_hotspots, buffer_size=0.002):
    """Create high-crime area polygons from filtered crime data."""
    crime_points = [Point(lon, lat) for lat, lon in crime_hotspots]
    if not crime_points:
        return None

    crime_buffers = [p.buffer(buffer_size) for p in crime_points]
    return unary_union(crime_buffers)  # Merge overlapping zones

def is_route_in_crime_zone(route_coords, crime_polygon):
    """Check if a route intersects with a high-crime zone."""
    route_line = LineString(route_coords)
    return route_line.intersects(crime_polygon)

def display_map(start, dest, route, alt_route, crime_hotspots_primary, crime_hotspots_alt, crime_zones):
    """Display the map with the main route, alternative route, and crime hotspots."""
    center = [(start[0] + dest[0]) / 2, (start[1] + dest[1]) / 2]
    crime_map = folium.Map(location=center, zoom_start=14)

    # Add start & destination markers
    folium.Marker(location=start, popup="Source Location", icon=folium.Icon(color="blue")).add_to(crime_map)
    folium.Marker(location=dest, popup="Destination", icon=folium.Icon(color="red")).add_to(crime_map)

    # Add primary route
    if route:
        route_coords = [(coord[1], coord[0]) for coord in route['features'][0]['geometry']['coordinates']]
        folium.PolyLine(route_coords, color="blue", weight=5, opacity=0.8, popup="Primary Route").add_to(crime_map)

    # Add alternative route
    if alt_route:
        alt_coords = [(coord[1], coord[0]) for coord in alt_route['features'][0]['geometry']['coordinates']]
        folium.PolyLine(alt_coords, color="green", weight=5, opacity=0.8, popup="Alternative Route").add_to(crime_map)
        print("✅ Alternative safer route found and displayed!")
    else:
        print("⚠ No alternative route found. Proceed with caution.")

    # Add crime hotspot markers for primary route (Red)
    marker_cluster_primary = MarkerCluster().add_to(crime_map)
    for crime in crime_hotspots_primary:
        folium.CircleMarker(
            location=crime,
            radius=0.125,
            color="black",
            fill=True,
            fill_color="red",
            fill_opacity=0.8,
            popup="Crime Hotspot (Primary Route)"
        ).add_to(marker_cluster_primary)

    # Add crime hotspot markers for alternative route (Yellow)
    marker_cluster_alt = MarkerCluster().add_to(crime_map)
    for crime in crime_hotspots_alt:
        folium.CircleMarker(
            location=crime,
            radius=0.125,
            color="black",
            fill=True,
            fill_color="yellow",
            fill_opacity=0.8,
            popup="Crime Hotspot (Alternative Route)"
        ).add_to(marker_cluster_alt)

    # Add crime zones to map
    if crime_zones:
        if isinstance(crime_zones, MultiPolygon):  # If multiple crime polygons exist
            for polygon in crime_zones.geoms:
                folium.Polygon(
                    locations=[(lat, lon) for lon, lat in polygon.exterior.coords],
                    color="red",
                    fill=True,
                    fill_color="darkred",
                    fill_opacity=0.4,
                    popup="High Crime Zone"
                ).add_to(crime_map)
        else:  # Single crime polygon
            folium.Polygon(
                locations=[(lat, lon) for lon, lat in crime_zones.exterior.coords],
                color="red",
                fill=True,
                fill_color="darkred",
                fill_opacity=0.4,
                popup="High Crime Zone"
            ).add_to(crime_map)

    # Save map
    crime_map.save("crime_route_with_alternative.html")
    print("✅ Map saved as crime_route_with_alternative.html")

def main():
    """Main execution function."""
    try:
        # Get user input for source and destination
        source_lat = float(input("Enter source latitude: "))
        source_lon = float(input("Enter source longitude: "))
        destination_lat = float(input("Enter destination latitude: "))
        destination_lon = float(input("Enter destination longitude: "))

        source = (source_lat, source_lon)
        destination = (destination_lat, destination_lon)

        # Get primary route
        primary_route = get_route(source, destination)

        if not primary_route:
            print("❌ No route found. Check coordinates or API key.")
            return

        # Extract primary route coordinates
        route_coords = [(coord[0], coord[1]) for coord in primary_route['features'][0]['geometry']['coordinates']]

        # Filter crime hotspots for primary route
        crime_hotspots_primary = filter_crimes_along_route(df, route_coords, buffer_distance=500)

        # Generate crime zones from primary route crimes
        crime_zones = create_crime_zones(crime_hotspots_primary)

        alternative_route = None
        crime_hotspots_alt = []

        if crime_zones and is_route_in_crime_zone(route_coords, crime_zones):
            print("⚠ WARNING: Your route passes through a high-crime area!")

            # Get alternative route avoiding crime zones
            alternative_route = get_route(source, destination, avoid_polygons=crime_zones)

            if alternative_route:
                print("✅ Alternative safer route found!")

                # Extract alternative route coordinates
                alt_route_coords = [(coord[0], coord[1]) for coord in alternative_route['features'][0]['geometry']['coordinates']]

                # Filter crime hotspots for alternative route
                crime_hotspots_alt = filter_crimes_along_route(df, alt_route_coords, buffer_distance=500)
            else:
                print("⚠ No alternative route available. Proceed with caution.")

        # Display final map
        display_map(source, destination, primary_route, alternative_route, crime_hotspots_primary, crime_hotspots_alt, crime_zones)

    except ValueError:
        print("❌ Error: Please enter valid coordinates")
    except Exception as e:
        print(f"❌ An error occurred: {str(e)}")

if __name__ == "__main__":
    main()







