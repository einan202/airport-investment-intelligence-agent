import tools.rank_expansion_candidates as expansion_module


def test_regional_ranking_filters_duplicate_state(monkeypatch):
    ranked_airports = []

    def fake_rank_expansion_candidates(airport_icaos):
        ranked_airports.extend(airport_icaos)

        return [
            {
                "airport": airport,
                "expansion_score": 0.5,
            }
            for airport in airport_icaos
        ]

    monkeypatch.setattr(
        expansion_module,
        "rank_expansion_candidates",
        fake_rank_expansion_candidates,
    )

    result = expansion_module.rank_regional_expansion_candidates(
        candidates=[
            {"icao": "KBOS"},
            {"icao": "KHYA"},
            {"icao": "KPVD"},
        ],
        allowed_states=[
            "Massachusetts",
            "Rhode Island",
        ],
    )

    assert result["missing_states"] == []

    assert ranked_airports == [
        "KBOS",
        "KPVD",
    ]

    assert len(result["ranking"]) == 2

    assert result["valid"][0]["icao"] == "KBOS"
    assert result["valid"][1]["icao"] == "KPVD"

    assert {"icao": "KHYA"} in result["invalid"]


def test_regional_ranking_does_not_rank_when_state_is_missing(
    monkeypatch,
):
    rank_called = False

    def fake_rank_expansion_candidates(airport_icaos):
        nonlocal rank_called
        rank_called = True
        return []

    monkeypatch.setattr(
        expansion_module,
        "rank_expansion_candidates",
        fake_rank_expansion_candidates,
    )

    result = expansion_module.rank_regional_expansion_candidates(
        candidates=[
            {"icao": "KBOS"},
        ],
        allowed_states=[
            "Massachusetts",
            "Rhode Island",
        ],
    )

    assert result["ranking"] == []
    assert result["missing_states"] == ["Rhode Island"]
    assert rank_called is False


def test_regional_ranking_passes_only_valid_airports_to_ranking(
    monkeypatch,
):
    validation_result = {
        "valid": [
            {
                "icao": "KBOS",
                "name": "General Edward Lawrence Logan International Airport",
                "state": "Massachusetts",
            },
            {
                "icao": "KPVD",
                "name": "Rhode Island T.F. Green International Airport",
                "state": "Rhode Island",
            },
        ],
        "invalid": [
            {"icao": "KHYA"},
        ],
        "missing_states": [],
    }

    monkeypatch.setattr(
        expansion_module,
        "validate_airport_candidates",
        lambda candidates, allowed_states: validation_result,
    )

    received_airports = []

    def fake_rank_expansion_candidates(airport_icaos):
        received_airports.extend(airport_icaos)

        return [
            {"airport": "KBOS", "expansion_score": 0.7},
            {"airport": "KPVD", "expansion_score": 0.4},
        ]

    monkeypatch.setattr(
        expansion_module,
        "rank_expansion_candidates",
        fake_rank_expansion_candidates,
    )

    result = expansion_module.rank_regional_expansion_candidates(
        candidates=[
            {"icao": "KBOS"},
            {"icao": "KHYA"},
            {"icao": "KPVD"},
        ],
        allowed_states=[
            "Massachusetts",
            "Rhode Island",
        ],
    )

    assert received_airports == [
        "KBOS",
        "KPVD",
    ]

    assert result["ranking"] == [
        {"airport": "KBOS", "expansion_score": 0.7},
        {"airport": "KPVD", "expansion_score": 0.4},
    ]