import os

import requests
from dotenv import load_dotenv


load_dotenv()

API_KEY = os.getenv("FLIGHT_API_KEY")

PAGE_SIZE = 50
MAX_PAGES = 3


def get_departures(airport_code: str):
    """Get departures from an airport by ICAO code."""

    url = "https://airlabs.co/api/v9/schedules"

    flights = []
    offset = 0

    for _ in range(MAX_PAGES):
        params = {
            "api_key": API_KEY,
            "dep_icao": airport_code,
            "limit": PAGE_SIZE,
            "offset": offset,
        }

        response = requests.get(
            url,
            params=params,
            timeout=(10, 30),
        )

        response.raise_for_status()

        data = response.json()

        if "error" in data:
            error = data["error"]

            raise RuntimeError(
                f"AirLabs API error: "
                f"{error.get('message', 'Unknown error')} "
                f"({error.get('code', 'unknown_code')})"
            )

        page_flights = data.get("response", [])

        if not page_flights:
            break

        flights.extend(page_flights)

        has_more = data.get("request", {}).get("has_more", False)

        if not has_more:
            break

        offset += 1

    return [
        {
            "flight_number": flight.get("flight_number"),
            "dep_icao": flight.get("dep_icao"),
            "arr_icao": flight.get("arr_icao"),
            "duration": flight.get("duration"),
            "status": flight.get("status"),
            "dep_delayed": flight.get("dep_delayed"),
            "arr_delayed": flight.get("arr_delayed"),
        }
        for flight in flights
    ]