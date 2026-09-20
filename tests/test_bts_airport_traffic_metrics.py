import pytest

from tools.get_bts_airport_traffic_metrics import (
    get_bts_airport_traffic_metrics,
)


pytestmark = pytest.mark.integration


REQUIRED_FIELDS = {
    "airport",
    "month",
    "departures",
    "passengers",
    "avg_load_factor",
}


def test_get_bts_airport_traffic_metrics_with_iata():
    rows = get_bts_airport_traffic_metrics("BOS", 2023)

    assert isinstance(rows, list)
    assert len(rows) > 0

    first_row = rows[0]

    assert isinstance(first_row, dict)
    assert REQUIRED_FIELDS.issubset(first_row.keys())
    assert first_row["airport"] == "BOS"
    assert first_row["departures"] >= 0
    assert first_row["passengers"] >= 0


def test_get_bts_airport_traffic_metrics_with_icao():
    rows = get_bts_airport_traffic_metrics("KBOS", 2023)

    assert isinstance(rows, list)
    assert len(rows) > 0

    first_row = rows[0]

    assert REQUIRED_FIELDS.issubset(first_row.keys())
    assert first_row["airport"] == "KBOS"
    assert first_row["departures"] >= 0
    assert first_row["passengers"] >= 0


def test_get_bts_airport_traffic_metrics_unknown_airport():
    rows = get_bts_airport_traffic_metrics("ZZZ", 2023)

    assert rows == []