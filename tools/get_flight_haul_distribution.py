import os
import requests
from dotenv import load_dotenv
from tools.get_departures import get_departures

load_dotenv()

API_KEY = os.getenv("FLIGHT_API_KEY")


SHORT_HAUL_MAX_MINUTES = 180
MEDIUM_HAUL_MAX_MINUTES = 360


def classify_flight_duration(duration):
    if duration < SHORT_HAUL_MAX_MINUTES:
        return "short"
    elif duration < MEDIUM_HAUL_MAX_MINUTES:
        return "medium"
    else:
        return "long"


def get_flight_haul_distribution(airport_icao):
    flights = get_departures(airport_icao)

    valid_flights = [
        flight for flight in flights
        if flight["duration"] is not None
        and flight["status"] != "cancelled"
    ]

    counts = {
        "short": 0,
        "medium": 0,
        "long": 0
    }

    for flight in valid_flights:
        category = classify_flight_duration(flight["duration"])
        counts[category] += 1

    total = len(valid_flights)

    if total == 0:
        return {
            "airport": airport_icao,
            "total_flights": 0,
            "short_haul": 0,
            "medium_haul": 0,
            "long_haul": 0,
            "short_haul_percentage": 0,
            "medium_haul_percentage": 0,
            "long_haul_percentage": 0
        }

    return {
        "airport": airport_icao,
        "total_flights": total,
        "short_haul": counts["short"],
        "medium_haul": counts["medium"],
        "long_haul": counts["long"],
        "short_haul_percentage": counts["short"] / total,
        "medium_haul_percentage": counts["medium"] / total,
        "long_haul_percentage": counts["long"] / total
    }