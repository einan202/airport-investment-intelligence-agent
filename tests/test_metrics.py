import pytest

import tools.get_departure_congestion_metrics as departure_module
import tools.get_arrivals_congestion_metrics as arrival_module
import tools.get_flight_congestion_metrics as overall_module
import tools.get_flight_haul_distribution as haul_module
import tools.rank_expansion_candidates as expansion_module

from tools.get_departure_congestion_metrics import (
    get_departure_congestion_metrics,
)
from tools.get_arrivals_congestion_metrics import (
    get_arrivals_congestion_metrics,
)
from tools.get_flight_congestion_metrics import (
    get_flight_congestion_metrics,
)
from tools.get_flight_haul_distribution import (
    classify_flight_duration,
    get_flight_haul_distribution,
)
from tools.rank_expansion_candidates import (
    rank_expansion_candidates,
)


def test_departure_congestion_metrics(monkeypatch):
    fake_flights = [
        {"status": "scheduled", "dep_delayed": 30},
        {"status": "scheduled", "dep_delayed": 60},
        {"status": "scheduled", "dep_delayed": 0},
        {"status": "cancelled", "dep_delayed": 0},
    ]

    monkeypatch.setattr(
        departure_module,
        "get_departures",
        lambda airport: fake_flights,
    )

    result = get_departure_congestion_metrics("TEST")

    assert result["airport"] == "TEST"
    assert result["total_flights"] == 4
    assert result["delayed_flights"] == 2
    assert result["delay_rate"] == pytest.approx(0.5)
    assert result["average_delay"] == pytest.approx(45)
    assert result["cancelled_flights"] == 1
    assert result["cancellation_rate"] == pytest.approx(0.25)
    assert result["congestion_score"] == pytest.approx(0.575)


def test_arrivals_congestion_metrics(monkeypatch):
    fake_flights = [
        {"status": "scheduled", "arr_delayed": 20},
        {"status": "scheduled", "arr_delayed": 40},
        {"status": "scheduled", "arr_delayed": 0},
        {"status": "scheduled", "arr_delayed": 0},
    ]

    monkeypatch.setattr(
        arrival_module,
        "get_arrivals",
        lambda airport: fake_flights,
    )

    result = get_arrivals_congestion_metrics("TEST")

    assert result["airport"] == "TEST"
    assert result["total_flights"] == 4
    assert result["delayed_flights"] == 2
    assert result["delay_rate"] == pytest.approx(0.5)
    assert result["average_delay"] == pytest.approx(30)
    assert result["cancelled_flights"] == 0
    assert result["cancellation_rate"] == pytest.approx(0)
    assert result["congestion_score"] == pytest.approx(0.5)


def test_overall_flight_congestion(monkeypatch):
    monkeypatch.setattr(
        overall_module,
        "get_departure_congestion_metrics",
        lambda airport: {
            "airport": airport,
            "congestion_score": 0.6,
            "total_flights": 100,
        },
    )

    monkeypatch.setattr(
        overall_module,
        "get_arrivals_congestion_metrics",
        lambda airport: {
            "airport": airport,
            "congestion_score": 0.4,
            "total_flights": 100,
        },
    )

    result = get_flight_congestion_metrics("TEST")

    assert result["airport"] == "TEST"
    assert result["flight_congestion_score"] == pytest.approx(0.52)
    assert result["departure"]["congestion_score"] == pytest.approx(0.6)
    assert result["arrival"]["congestion_score"] == pytest.approx(0.4)


def test_classify_flight_duration():
    assert classify_flight_duration(120) == "short"
    assert classify_flight_duration(179) == "short"
    assert classify_flight_duration(180) == "medium"
    assert classify_flight_duration(359) == "medium"
    assert classify_flight_duration(360) == "long"
    assert classify_flight_duration(500) == "long"


def test_flight_haul_distribution(monkeypatch):
    fake_flights = [
        {"duration": 120, "status": "scheduled"},
        {"duration": 240, "status": "scheduled"},
        {"duration": 400, "status": "scheduled"},
        {"duration": None, "status": "scheduled"},
        {"duration": 500, "status": "cancelled"},
    ]

    monkeypatch.setattr(
        haul_module,
        "get_departures",
        lambda airport: fake_flights,
    )

    result = get_flight_haul_distribution("TEST")

    assert result["airport"] == "TEST"
    assert result["total_flights"] == 3
    assert result["short_haul"] == 1
    assert result["medium_haul"] == 1
    assert result["long_haul"] == 1
    assert result["short_haul_percentage"] == pytest.approx(1 / 3)
    assert result["medium_haul_percentage"] == pytest.approx(1 / 3)
    assert result["long_haul_percentage"] == pytest.approx(1 / 3)


def test_rank_expansion_candidates(monkeypatch):
    fake_metrics = {
        "AAA": {
            "flight_congestion_score": 0.6,
            "departure": {"total_flights": 100},
            "arrival": {"total_flights": 100},
        },
        "BBB": {
            "flight_congestion_score": 0.3,
            "departure": {"total_flights": 50},
            "arrival": {"total_flights": 50},
        },
    }

    monkeypatch.setattr(
        expansion_module,
        "resolve_airport_to_icao",
        lambda airport: airport,
    )

    monkeypatch.setattr(
        expansion_module,
        "get_flight_congestion_metrics",
        lambda airport: fake_metrics[airport],
    )

    result = rank_expansion_candidates(["AAA", "BBB"])

    assert len(result) == 2

    assert result[0]["airport"] == "AAA"
    assert result[0]["total_flights"] == 200
    assert result[0]["normalized_volume"] == pytest.approx(1.0)
    assert result[0]["expansion_score"] == pytest.approx(0.76)

    assert result[1]["airport"] == "BBB"
    assert result[1]["total_flights"] == 100
    assert result[1]["normalized_volume"] == pytest.approx(0.5)
    assert result[1]["expansion_score"] == pytest.approx(0.38)


def test_departure_congestion_no_flights(monkeypatch):
    monkeypatch.setattr(
        departure_module,
        "get_departures",
        lambda airport: [],
    )

    result = get_departure_congestion_metrics("TEST")

    assert result["total_flights"] == 0
    assert result["delayed_flights"] == 0
    assert result["delay_rate"] == 0
    assert result["average_delay"] == 0
    assert result["cancelled_flights"] == 0
    assert result["cancellation_rate"] == 0
    assert result["congestion_score"] == 0


def test_departure_congestion_no_delays(monkeypatch):
    fake_flights = [
        {"status": "scheduled", "dep_delayed": 0},
        {"status": "scheduled", "dep_delayed": 0},
        {"status": "scheduled", "dep_delayed": 0},
    ]

    monkeypatch.setattr(
        departure_module,
        "get_departures",
        lambda airport: fake_flights,
    )

    result = get_departure_congestion_metrics("TEST")

    assert result["total_flights"] == 3
    assert result["delayed_flights"] == 0
    assert result["delay_rate"] == 0
    assert result["average_delay"] == 0
    assert result["congestion_score"] == 0


def test_departure_congestion_all_cancelled(monkeypatch):
    fake_flights = [
        {"status": "cancelled", "dep_delayed": 0},
        {"status": "cancelled", "dep_delayed": 0},
    ]

    monkeypatch.setattr(
        departure_module,
        "get_departures",
        lambda airport: fake_flights,
    )

    result = get_departure_congestion_metrics("TEST")

    assert result["total_flights"] == 2
    assert result["cancelled_flights"] == 2
    assert result["cancellation_rate"] == pytest.approx(1.0)

    # Cancellation is reported separately and is not part of the score.
    assert result["congestion_score"] == 0


def test_flight_haul_ignores_missing_duration_and_cancelled(monkeypatch):
    fake_flights = [
        {"duration": None, "status": "scheduled"},
        {"duration": 120, "status": "cancelled"},
        {"duration": 400, "status": "scheduled"},
    ]

    monkeypatch.setattr(
        haul_module,
        "get_departures",
        lambda airport: fake_flights,
    )

    result = get_flight_haul_distribution("TEST")

    assert result["total_flights"] == 1
    assert result["short_haul"] == 0
    assert result["medium_haul"] == 0
    assert result["long_haul"] == 1
    assert result["short_haul_percentage"] == 0
    assert result["medium_haul_percentage"] == 0
    assert result["long_haul_percentage"] == pytest.approx(1.0)


def test_flight_haul_no_valid_flights(monkeypatch):
    fake_flights = [
        {"duration": None, "status": "scheduled"},
        {"duration": 500, "status": "cancelled"},
    ]

    monkeypatch.setattr(
        haul_module,
        "get_departures",
        lambda airport: fake_flights,
    )

    result = get_flight_haul_distribution("TEST")

    assert result["total_flights"] == 0
    assert result["short_haul"] == 0
    assert result["medium_haul"] == 0
    assert result["long_haul"] == 0
    assert result["short_haul_percentage"] == 0
    assert result["medium_haul_percentage"] == 0
    assert result["long_haul_percentage"] == 0


def test_equal_expansion_scores(monkeypatch):
    fake_metrics = {
        "AAA": {
            "flight_congestion_score": 0.5,
            "departure": {"total_flights": 100},
            "arrival": {"total_flights": 100},
        },
        "BBB": {
            "flight_congestion_score": 0.5,
            "departure": {"total_flights": 100},
            "arrival": {"total_flights": 100},
        },
    }

    monkeypatch.setattr(
        expansion_module,
        "resolve_airport_to_icao",
        lambda airport: airport,
    )

    monkeypatch.setattr(
        expansion_module,
        "get_flight_congestion_metrics",
        lambda airport: fake_metrics[airport],
    )

    result = rank_expansion_candidates(["AAA", "BBB"])

    assert len(result) == 2
    assert {item["airport"] for item in result} == {"AAA", "BBB"}
    assert result[0]["expansion_score"] == pytest.approx(0.7)
    assert result[1]["expansion_score"] == pytest.approx(0.7)