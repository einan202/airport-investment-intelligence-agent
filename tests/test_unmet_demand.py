import pytest

import tools.estimate_unmet_demand as unmet_module
from tools.estimate_unmet_demand import estimate_unmet_demand


def test_estimate_unmet_demand(monkeypatch):
    current_rows = [
        {
            "passengers": 1760,
            "seats": 2100,
        }
    ]

    previous_rows = [
        {
            "passengers": 1600,
            "seats": 2000,
        }
    ]

    def fake_bts(airport, year):
        if year == 2023:
            return current_rows

        return previous_rows

    monkeypatch.setattr(
        unmet_module,
        "get_bts_airport_traffic_metrics",
        fake_bts,
    )

    monkeypatch.setattr(
        unmet_module,
        "get_flight_congestion_metrics",
        lambda airport: {
            "flight_congestion_score": 0.5
        },
    )

    result = estimate_unmet_demand("KSFO", 2023)

    assert result["airport"] == "KSFO"
    assert result["year"] == 2023
    assert result["passengers"] == 1760
    assert result["seats"] == 2100

    # 1760 / 2100
    assert result["seat_utilization"] == pytest.approx(1760 / 2100)

    # (1760 - 1600) / 1600 = 10%
    assert result["passenger_growth"] == pytest.approx(0.10)

    # (2100 - 2000) / 2000 = 5%
    assert result["seat_growth"] == pytest.approx(0.05)

    # 10% passenger growth - 5% seat growth = 5%
    assert result["passenger_vs_seat_growth_gap"] == pytest.approx(0.05)

    assert result["flight_congestion_score"] == pytest.approx(0.5)

    # load_score = 1760 / 2100
    # capacity_gap_score = 0.05 / 0.10 = 0.5
    # congestion_score = 0.5
    expected_score = (
        0.5 * (1760 / 2100)
        + 0.3 * 0.5
        + 0.2 * 0.5
    )

    assert result["unmet_demand_score"] == pytest.approx(expected_score)


def test_no_previous_data(monkeypatch):
    monkeypatch.setattr(
        unmet_module,
        "get_bts_airport_traffic_metrics",
        lambda airport, year: (
            [
                {
                    "passengers": 1000,
                    "seats": 1250,
                }
            ]
            if year == 2023
            else []
        ),
    )

    monkeypatch.setattr(
        unmet_module,
        "get_flight_congestion_metrics",
        lambda airport: {
            "flight_congestion_score": 0.5
        },
    )

    result = estimate_unmet_demand("KSFO", 2023)

    assert result["passenger_growth"] == 0
    assert result["seat_growth"] == 0
    assert result["passenger_vs_seat_growth_gap"] == 0
    assert result["seat_utilization"] == pytest.approx(0.8)

    # 0.5 * 0.8 + 0.3 * 0 + 0.2 * 0.5
    assert result["unmet_demand_score"] == pytest.approx(0.5)


def test_negative_passenger_vs_seat_growth_gap_does_not_reduce_score(
    monkeypatch,
):
    def fake_bts(airport, year):
        if year == 2023:
            return [
                {
                    "passengers": 900,
                    "seats": 1200,
                }
            ]

        return [
            {
                "passengers": 1000,
                "seats": 1000,
            }
        ]

    monkeypatch.setattr(
        unmet_module,
        "get_bts_airport_traffic_metrics",
        fake_bts,
    )

    monkeypatch.setattr(
        unmet_module,
        "get_flight_congestion_metrics",
        lambda airport: {
            "flight_congestion_score": 0.5
        },
    )

    result = estimate_unmet_demand("KSFO", 2023)

    assert result["passenger_growth"] == pytest.approx(-0.10)
    assert result["seat_growth"] == pytest.approx(0.20)
    assert result["passenger_vs_seat_growth_gap"] == pytest.approx(-0.30)

    # Negative growth gap becomes a capacity_gap_score of 0.
    # seat utilization = 900 / 1200 = 0.75
    # 0.5 * 0.75 + 0.2 * 0.5 = 0.475
    assert result["unmet_demand_score"] == pytest.approx(0.475)


def test_no_current_bts_data(monkeypatch):
    monkeypatch.setattr(
        unmet_module,
        "get_bts_airport_traffic_metrics",
        lambda airport, year: [],
    )

    monkeypatch.setattr(
        unmet_module,
        "get_flight_congestion_metrics",
        lambda airport: {
            "flight_congestion_score": 0.5
        },
    )

    with pytest.raises(ValueError):
        estimate_unmet_demand("KSFO", 2023)