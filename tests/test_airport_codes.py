import pytest

from tools.airport_codes import (
    normalize_to_bts_airport_code,
    resolve_airport_to_icao,
    validate_airport_candidates,
)


def test_normalize_iata_code():
    assert normalize_to_bts_airport_code("BOS") == "BOS"


def test_normalize_iata_code_lowercase():
    assert normalize_to_bts_airport_code("bos") == "BOS"


def test_normalize_icao_code():
    assert normalize_to_bts_airport_code("KBOS") == "BOS"


def test_normalize_icao_code_lowercase():
    assert normalize_to_bts_airport_code("kbos") == "BOS"


def test_normalize_unknown_icao():
    with pytest.raises(ValueError):
        normalize_to_bts_airport_code("ZZZZ")


def test_normalize_invalid_code():
    with pytest.raises(ValueError):
        normalize_to_bts_airport_code("INVALID")


def test_resolve_icao():
    assert resolve_airport_to_icao("KBOS") == "KBOS"


def test_resolve_icao_lowercase():
    assert resolve_airport_to_icao("kbos") == "KBOS"


def test_resolve_iata():
    assert resolve_airport_to_icao("BOS") == "KBOS"


def test_resolve_iata_lowercase():
    assert resolve_airport_to_icao("bos") == "KBOS"


def test_resolve_empty_query():
    with pytest.raises(ValueError):
        resolve_airport_to_icao("")


def test_resolve_unknown_airport():
    with pytest.raises(ValueError):
        resolve_airport_to_icao("ZZZZ")


def test_validate_airport_candidates():
    candidates = [
        {"icao": "KBOS"},
        {"icao": "KBDL"},
        {"icao": "KLEX"},
        {"icao": "ZZZZ"},
    ]

    result = validate_airport_candidates(
        candidates,
        [
            "Massachusetts",
            "Connecticut",
        ],
    )

    assert [airport["icao"] for airport in result["valid"]] == [
        "KBOS",
        "KBDL",
    ]

    assert len(result["invalid"]) == 2
    assert result["missing_states"] == []


def test_validate_airport_candidates_accepts_iata():
    result = validate_airport_candidates(
        [
            {"icao": "BOS"},
            {"icao": "BDL"},
        ],
        [
            "Massachusetts",
            "Connecticut",
        ],
    )

    assert [airport["icao"] for airport in result["valid"]] == [
        "KBOS",
        "KBDL",
    ]

    assert result["invalid"] == []
    assert result["missing_states"] == []


def test_validate_airport_candidates_reports_missing_states():
    result = validate_airport_candidates(
        [
            {"icao": "KBOS"},
            {"icao": "KBDL"},
        ],
        [
            "Massachusetts",
            "Connecticut",
            "Maine",
            "Vermont",
        ],
    )

    assert result["missing_states"] == [
        "Maine",
        "Vermont",
    ]


def test_validate_airport_candidates_rejects_airport_outside_allowed_states():
    result = validate_airport_candidates(
        [
            {"icao": "KLAX"},
        ],
        [
            "Massachusetts",
        ],
    )

    assert result["valid"] == []
    assert result["invalid"] == [
        {"icao": "KLAX"},
    ]
    assert result["missing_states"] == [
        "Massachusetts",
    ]


def test_validate_airport_candidates_keeps_only_one_airport_per_state():
    result = validate_airport_candidates(
        [
            {"icao": "KBOS"},
            {"icao": "KHYA"},
            {"icao": "KBDL"},
        ],
        [
            "Massachusetts",
            "Connecticut",
        ],
    )

    assert [airport["icao"] for airport in result["valid"]] == [
        "KBOS",
        "KBDL",
    ]

    assert {"icao": "KHYA"} in result["invalid"]
    assert result["missing_states"] == []