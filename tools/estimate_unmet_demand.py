from tools.get_bts_airport_traffic_metrics import get_bts_airport_traffic_metrics
from tools.get_flight_congestion_metrics import get_flight_congestion_metrics


def estimate_unmet_demand(airport_code: str, year: int):
    current_rows = get_bts_airport_traffic_metrics(airport_code, year)
    previous_rows = get_bts_airport_traffic_metrics(airport_code, year - 1)

    if not current_rows:
        raise ValueError(f"No BTS data found for {airport_code} in {year}")

    current_passengers = sum(row["passengers"] for row in current_rows)
    previous_passengers = sum(row["passengers"] for row in previous_rows)

    current_seats = sum(row["seats"] for row in current_rows)
    previous_seats = sum(row["seats"] for row in previous_rows)

    seat_utilization = (
        current_passengers / current_seats
        if current_seats > 0
        else 0
    )

    passenger_growth = (
        (current_passengers - previous_passengers) / previous_passengers
        if previous_passengers > 0
        else 0
    )

    seat_growth = (
        (current_seats - previous_seats) / previous_seats
        if previous_seats > 0
        else 0
    )

    passenger_vs_seat_growth_gap = passenger_growth - seat_growth

    congestion = get_flight_congestion_metrics(airport_code)
    congestion_score = congestion["flight_congestion_score"]

    load_score = min(max(seat_utilization, 0), 1)

    # A 10 percentage-point gap between passenger growth and
    # seat-capacity growth is treated as strong demand pressure.
    capacity_gap_score = min(
        max(passenger_vs_seat_growth_gap / 0.10, 0),
        1,
    )

    unmet_demand_score = (
        0.5 * load_score
        + 0.3 * capacity_gap_score
        + 0.2 * congestion_score
    )

    return {
        "airport": airport_code,
        "year": year,
        "passengers": current_passengers,
        "seats": current_seats,
        "seat_utilization": seat_utilization,
        "passenger_growth": passenger_growth,
        "seat_growth": seat_growth,
        "passenger_vs_seat_growth_gap": passenger_vs_seat_growth_gap,
        "flight_congestion_score": congestion_score,
        "unmet_demand_score": unmet_demand_score,
    }