from tools.airport_codes import (
    resolve_airport_to_icao,
    validate_airport_candidates,
)
from tools.get_flight_congestion_metrics import get_flight_congestion_metrics


def rank_expansion_candidates(airport_icaos):
    airports = []

    for airport_code in airport_icaos:
        airport_icao = resolve_airport_to_icao(airport_code)

        congestion = get_flight_congestion_metrics(airport_icao)

        total_flights = (
            congestion["departure"]["total_flights"]
            + congestion["arrival"]["total_flights"]
        )

        airports.append({
            "airport": airport_icao,
            "total_flights": total_flights,
            "flight_congestion_score":
                congestion["flight_congestion_score"],
        })

    if not airports:
        return []

    max_flights = max(
        airport["total_flights"]
        for airport in airports
    )

    for airport in airports:
        normalized_volume = (
            airport["total_flights"] / max_flights
            if max_flights > 0
            else 0
        )

        expansion_score = (
            0.6 * airport["flight_congestion_score"]
            + 0.4 * normalized_volume
        )

        airport["normalized_volume"] = normalized_volume
        airport["expansion_score"] = expansion_score

    return sorted(
        airports,
        key=lambda airport: airport["expansion_score"],
        reverse=True,
    )


def rank_regional_expansion_candidates(
    candidates: list[dict],
    allowed_states: list[str],
):
    validation = validate_airport_candidates(
        candidates=candidates,
        allowed_states=allowed_states,
    )

    if validation["missing_states"]:
        return {
            "ranking": [],
            "valid": validation["valid"],
            "invalid": validation["invalid"],
            "missing_states": validation["missing_states"],
        }

    valid_airports = [
        candidate["icao"]
        for candidate in validation["valid"]
    ]

    ranking = rank_expansion_candidates(valid_airports)

    return {
        "ranking": ranking,
        "valid": validation["valid"],
        "invalid": validation["invalid"],
        "missing_states": [],
    }