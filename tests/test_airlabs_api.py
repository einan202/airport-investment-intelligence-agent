import os

import pytest
from dotenv import load_dotenv

from tools.get_departures import get_departures
from tools.get_arrivals import get_arrivals


load_dotenv()

REQUIRED_FIELDS = {
    "flight_number",
    "dep_icao",
    "arr_icao",
    "duration",
    "status",
    "dep_delayed",
    "arr_delayed",
}


pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        not os.getenv("FLIGHT_API_KEY"),
        reason="FLIGHT_API_KEY is not configured",
    ),
]


def test_get_departures():
    flights = get_departures("KBOS")

    assert isinstance(flights, list)
    assert len(flights) > 0

    first_flight = flights[0]

    assert isinstance(first_flight, dict)
    assert REQUIRED_FIELDS.issubset(first_flight.keys())


def test_get_arrivals():
    flights = get_arrivals("KBOS")

    assert isinstance(flights, list)
    assert len(flights) > 0

    first_flight = flights[0]

    assert isinstance(first_flight, dict)
    assert REQUIRED_FIELDS.issubset(first_flight.keys())


def test_invalid_airport():
    assert get_departures("XXXX") == []
    assert get_arrivals("XXXX") == []