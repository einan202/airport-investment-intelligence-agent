import airportsdata


AIRPORTS_BY_ICAO = airportsdata.load("ICAO")


def normalize_to_bts_airport_code(airport_code: str) -> str:
    airport_code = airport_code.strip().upper()

    if len(airport_code) == 3:
        return airport_code

    if len(airport_code) == 4:
        airport = AIRPORTS_BY_ICAO.get(airport_code)

        if not airport:
            raise ValueError(f"Unknown ICAO airport code: {airport_code}")

        iata_code = airport.get("iata")

        if not iata_code:
            raise ValueError(
                f"Airport {airport_code} does not have an IATA code"
            )

        return iata_code

    raise ValueError(f"Invalid airport code: {airport_code}")


def resolve_airport_to_icao(query: str) -> str:
    query = query.strip()

    if not query:
        raise ValueError("Airport query cannot be empty")

    upper_query = query.upper()
    lower_query = query.lower()

    if len(upper_query) == 4 and upper_query in AIRPORTS_BY_ICAO:
        return upper_query

    matches = []

    for icao_code, airport in AIRPORTS_BY_ICAO.items():
        iata = (airport.get("iata") or "").upper()
        name = (airport.get("name") or "").lower()
        city = (airport.get("city") or "").lower()

        if len(upper_query) == 3 and iata == upper_query:
            return icao_code

        if lower_query == name or lower_query == city:
            matches.append({
                "icao": icao_code,
                "iata": iata,
                "name": airport.get("name"),
                "city": airport.get("city"),
            })

    if len(matches) == 1:
        return matches[0]["icao"]

    if len(matches) > 1:
        candidates = ", ".join(
            f'{airport["name"]} ({airport["icao"]}/{airport["iata"]})'
            for airport in matches
        )

        raise ValueError(
            f"Multiple airports found for '{query}': {candidates}"
        )

    raise ValueError(f"No airport found for '{query}'")


def validate_airport_candidates(
    candidates: list[dict],
    allowed_states: list[str],
) -> dict:
    original_states = [
        state.strip()
        for state in allowed_states
    ]

    allowed_states_lower = {
        state.lower()
        for state in original_states
    }

    valid = []
    invalid = []
    seen_states = set()

    for candidate in candidates:
        code = candidate["icao"].strip().upper()

        try:
            icao = resolve_airport_to_icao(code)
        except ValueError:
            invalid.append(candidate)
            continue

        airport = AIRPORTS_BY_ICAO[icao]

        state = airport.get("subd")

        if not state:
            invalid.append(candidate)
            continue

        state_lower = state.lower()

        if state_lower not in allowed_states_lower:
            invalid.append(candidate)
            continue

        if state_lower in seen_states:
            invalid.append(candidate)
            continue

        seen_states.add(state_lower)

        valid.append({
            "icao": icao,
            "name": airport.get("name"),
            "state": state,
        })

    missing_states = [
        state
        for state in original_states
        if state.lower() not in seen_states
    ]

    return {
        "valid": valid,
        "invalid": invalid,
        "missing_states": missing_states,
    }