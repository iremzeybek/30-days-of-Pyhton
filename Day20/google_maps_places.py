import requests
import pandas as pd
import math
from datetime import datetime

# =========================================================
# GOOGLE MAPS API CONFIGURATION
# =========================================================

API_KEY = "YOUR_GOOGLE_MAPS_API_KEY"

GEOCODE_URL = "https://maps.googleapis.com/maps/api/geocode/json"
PLACES_URL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"

# =========================================================
# GEOCODING FUNCTION
# =========================================================

def geocode_address(address):
    params = {
        "address": address,
        "key": API_KEY
    }

    response = requests.get(GEOCODE_URL, params=params)
    data = response.json()

    if data["status"] != "OK":
        raise Exception(f"Geocoding failed: {data['status']}")

    result = data["results"][0]

    location = result["geometry"]["location"]

    return {
        "formatted_address": result["formatted_address"],
        "lat": location["lat"],
        "lng": location["lng"]
    }

# =========================================================
# HAVERSINE DISTANCE CALCULATION
# =========================================================

def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in km

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)

    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = (
        math.sin(dphi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return round(R * c, 2)

# =========================================================
# PLACES SEARCH FUNCTION
# =========================================================

def search_nearby_places(lat, lng, place_type="cafe", radius=2000):
    params = {
        "location": f"{lat},{lng}",
        "radius": radius,
        "type": place_type,
        "key": API_KEY
    }

    response = requests.get(PLACES_URL, params=params)
    data = response.json()

    if data["status"] not in ["OK", "ZERO_RESULTS"]:
        raise Exception(f"Places search failed: {data['status']}")

    return data.get("results", [])

# =========================================================
# DATA PROCESSING
# =========================================================

def build_places_dataframe(origin_lat, origin_lng, places):
    rows = []

    for place in places:
        name = place.get("name", "N/A")

        vicinity = place.get("vicinity", "N/A")

        rating = place.get("rating", None)

        location = place.get("geometry", {}).get("location", {})

        place_lat = location.get("lat")
        place_lng = location.get("lng")

        if place_lat is None or place_lng is None:
            continue

        distance_km = haversine_distance(
            origin_lat,
            origin_lng,
            place_lat,
            place_lng
        )

        rows.append({
            "name": name,
            "address": vicinity,
            "rating": rating,
            "latitude": place_lat,
            "longitude": place_lng,
            "distance_km": distance_km
        })

    df = pd.DataFrame(rows)

    if not df.empty:
        df = df.sort_values(by=["distance_km", "rating"], ascending=[True, False])

    return df

# =========================================================
# SAVE RESULTS
# =========================================================

def save_results(df):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    filename = f"places_results_{timestamp}.csv"

    df.to_csv(filename, index=False)

    return filename

# =========================================================
# MAIN APPLICATION
# =========================================================

def main():
    print("Google Maps Geocoding & Places API Demo")
    print("-" * 50)

    address = input("Enter an address: ").strip()

    place_type = input(
        "Enter place type (cafe, restaurant, hospital, pharmacy): "
    ).strip()

    if not place_type:
        place_type = "cafe"

    radius_input = input("Search radius in meters [2000]: ").strip()

    radius = int(radius_input) if radius_input else 2000

    print("\nGeocoding address...")

    location = geocode_address(address)

    print(f"Address: {location['formatted_address']}")
    print(f"Latitude: {location['lat']}")
    print(f"Longitude: {location['lng']}")

    print(f"\nSearching nearby {place_type}s within {radius} meters...")

    places = search_nearby_places(
        location["lat"],
        location["lng"],
        place_type=place_type,
        radius=radius
    )

    if not places:
        print("No places found.")
        return

    df = build_places_dataframe(
        location["lat"],
        location["lng"],
        places
    )

    print(f"\nFound {len(df)} places:\n")

    print(df[["name", "rating", "distance_km"]].head(10).to_string(index=False))

    filename = save_results(df)

    print(f"\nResults saved to: {filename}")

if __name__ == "__main__":
    main()
