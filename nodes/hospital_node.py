import requests
import math
from typing import Dict, Any


def get_geoip_location():
    response = requests.get("http://ip-api.com/json/")
    data = response.json()

    if data["status"] != "success":
        raise RuntimeError("Failed to fetch GeoIP location")

    return {
        "lat": data["lat"],
        "lon": data["lon"],
        "city": data["city"],
        "country": data["country"]
    }


def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # km
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


def get_nearby_hospitals(lat, lon, radius_km=5):
    overpass_url = "https://overpass-api.de/api/interpreter"

    query = f"""
    [out:json];
    node
      ["amenity"="hospital"]
      (around:{radius_km * 1000},{lat},{lon});
    out;
    """

    response = requests.post(overpass_url, data={"data": query})
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


def hospital_node(state: Dict[str, Any]) -> Dict[str, Any]:
    location = get_geoip_location()
    hospitals = get_nearby_hospitals(location["lat"], location["lon"])

    severity = state["vision_json"]["clinical_indicators"]["severity_score"]

    if severity >= 8:
        urgency = "EMERGENCY"
        advice = "Seek emergency medical care immediately."
    elif severity >= 5:
        urgency = "URGENT"
        advice = "Visit a hospital or urgent care facility as soon as possible."
    else:
        urgency = "MEDICAL_REVIEW"
        advice = "Consult a healthcare provider for further evaluation."

    return {
        "final_output": {
            "action": "SEEK_MEDICAL_CARE",
            "urgency": urgency,
            "advice": advice,
            "user_location": location,
            "nearby_hospitals": hospitals
        }
    }
