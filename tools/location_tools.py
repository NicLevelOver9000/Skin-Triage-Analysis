import json
import math
import requests
from typing import Dict, Any
from azure_client import get_client, get_deployment

client = get_client()
deployment = get_deployment()


# ==========================================================
# 🧭 GEO LOCATION (IP-based)
# ==========================================================
def get_geoip_location() -> Dict[str, Any]:
    response = requests.get("http://ip-api.com/json/", timeout=5)
    data = response.json()

    if data.get("status") != "success":
        raise RuntimeError("Failed to fetch GeoIP location")

    return {
        "lat": data["lat"],
        "lon": data["lon"],
        "city": data["city"],
        "country": data["country"]
    }


# ==========================================================
# 📏 DISTANCE CALCULATION (Haversine)
# ==========================================================
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in km

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


# ==========================================================
# 🏥 FIND NEARBY HOSPITALS (OpenStreetMap Overpass)
# ==========================================================
def get_nearby_hospitals(lat, lon, radius_km=10):
    overpass_url = "https://overpass-api.de/api/interpreter"

    query = f"""
    [out:json];
    node
      ["amenity"="hospital"]
      (around:{radius_km * 1000},{lat},{lon});
    out;
    """

    response = requests.post(overpass_url, data={"data": query}, timeout=10)
    data = response.json()

    hospitals = []

    for element in data.get("elements", []):
        hospital_lat = element["lat"]
        hospital_lon = element["lon"]

        distance = haversine(lat, lon, hospital_lat, hospital_lon)

        hospitals.append({
            "name": element.get("tags", {}).get("name", "Unnamed Hospital"),
            "distance_km": round(distance, 2),
            "latitude": hospital_lat,
            "longitude": hospital_lon
        })

    hospitals.sort(key=lambda x: x["distance_km"])

    return hospitals[:5]
