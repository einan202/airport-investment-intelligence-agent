import requests

from tools.airport_codes import normalize_to_bts_airport_code


BTS_BASE_URL = "https://data.transportation.gov/resource"
T100_BY_ORIGIN_AIRPORT_DATASET = "r495-tyji"


def get_bts_airport_traffic_metrics(airport_code: str, year: int):
    """Get monthly BTS traffic metrics for an airport."""

    bts_airport_code = normalize_to_bts_airport_code(airport_code)

    url = f"{BTS_BASE_URL}/{T100_BY_ORIGIN_AIRPORT_DATASET}.json"

    params = {
        "$select": (
            "reporting_month, "
            "sum(total_departures) as departures, "
            "sum(total_passengers) as passengers, "
            "sum(total_seats) as seats, "
            "avg(total_load_factor) as avg_load_factor"
        ),
        "$where": (
            f"origin_airport_code='{bts_airport_code}' "
            f"AND year='{year}'"
        ),
        "$group": "reporting_month",
        "$order": "reporting_month",
        "$limit": 50000,
    }

    response = requests.get(
        url,
        params=params,
        timeout=10,
    )

    response.raise_for_status()

    rows = response.json()

    return [
        {
            "airport": airport_code.upper(),
            "month": row.get("reporting_month"),
            "departures": int(float(row.get("departures", 0))),
            "passengers": int(float(row.get("passengers", 0))),
            "seats": int(float(row.get("seats", 0))),
            "avg_load_factor": float(row.get("avg_load_factor", 0)),
        }
        for row in rows
    ]
