from tools.get_departure_congestion_metrics import get_departure_congestion_metrics
from tools.get_arrivals_congestion_metrics import get_arrivals_congestion_metrics

def get_flight_congestion_metrics(airport_icao):
    departure = get_departure_congestion_metrics(airport_icao)
    arrival = get_arrivals_congestion_metrics(airport_icao)

    flight_congestion_score = (
        0.6 * departure["congestion_score"] +
        0.4 * arrival["congestion_score"]
    )

    return {
        "airport": airport_icao,

        "flight_congestion_score": flight_congestion_score,

        "departure": departure,
        "arrival": arrival
    }