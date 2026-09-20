from tools.get_flight_congestion_metrics import get_flight_congestion_metrics
from tools.get_arrivals_congestion_metrics import get_arrivals_congestion_metrics
from tools.get_departure_congestion_metrics import get_departure_congestion_metrics
from tools.get_flight_haul_distribution import get_flight_haul_distribution
from tools.rank_expansion_candidates import (
    rank_expansion_candidates,
    rank_regional_expansion_candidates,
)
from tools.estimate_unmet_demand import estimate_unmet_demand


tools = [
    {
        "type": "function",
        "function": {
            "name": "get_flight_congestion_metrics",
            "description": (
                "Get overall deterministic operational flight congestion metrics "
                "for an airport using both departure and arrival delays. "
                "Use this for general airport congestion questions or comparisons. "
                "Do not use it when the user explicitly asks only about arrivals "
                "or only about departures."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "airport_icao": {
                        "type": "string",
                        "description": (
                            "Airport ICAO code, for example KLAX, KSFO, or KSNA."
                        ),
                    }
                },
                "required": ["airport_icao"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_arrivals_congestion_metrics",
            "description": (
                "Get deterministic arrival congestion metrics for an airport. "
                "Use this only when the user explicitly asks about arrivals, "
                "landings, or arrival delays. "
                "The returned flights represent a bounded operational sample, "
                "not a complete historical daily or monthly total."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "airport_icao": {
                        "type": "string",
                        "description": (
                            "Airport ICAO code, for example KLAX, KSFO, or KSNA."
                        ),
                    }
                },
                "required": ["airport_icao"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_departure_congestion_metrics",
            "description": (
                "Get deterministic departure congestion metrics for an airport. "
                "Use this only when the user explicitly asks about departures, "
                "takeoffs, or departure delays. "
                "The returned flights represent a bounded operational sample, "
                "not a complete historical daily or monthly total."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "airport_icao": {
                        "type": "string",
                        "description": (
                            "Airport ICAO code, for example KLAX, KSFO, or KSNA."
                        ),
                    }
                },
                "required": ["airport_icao"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_flight_haul_distribution",
            "description": (
                "Get the count and percentage of short-, medium-, and "
                "long-haul departing flights from an airport."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "airport_icao": {
                        "type": "string",
                        "description": (
                            "Airport ICAO code, for example PANC for Anchorage."
                        ),
                    }
                },
                "required": ["airport_icao"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "rank_expansion_candidates",
            "description": (
                "Rank an explicitly provided list of airports as potential "
                "expansion candidates using deterministic operational congestion "
                "and observed flight activity. "
                "Use this for direct airport comparisons. "
                "For regional questions involving states, use "
                "rank_regional_expansion_candidates instead."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "airport_icaos": {
                        "type": "array",
                        "items": {
                            "type": "string",
                        },
                        "description": (
                            "List of airport ICAO codes to compare."
                        ),
                    }
                },
                "required": ["airport_icaos"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "rank_regional_expansion_candidates",
            "description": (
                "Validate and rank airport candidates for a regional expansion "
                "question. The tool validates candidate airport locations, "
                "enforces at most one valid airport per allowed US state, and "
                "only performs the expansion ranking when every allowed state "
                "has a valid candidate. Use this tool for regional questions "
                "such as New England expansion analysis."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "candidates": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "icao": {
                                    "type": "string",
                                    "description": (
                                        "Proposed airport ICAO code."
                                    ),
                                }
                            },
                            "required": ["icao"],
                        },
                        "description": (
                            "Proposed representative airport candidates."
                        ),
                    },
                    "allowed_states": {
                        "type": "array",
                        "items": {
                            "type": "string",
                        },
                        "description": (
                            "Full US state names that belong to the requested "
                            "region, for example Massachusetts or Connecticut."
                        ),
                    },
                },
                "required": ["candidates", "allowed_states"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "estimate_unmet_demand",
            "description": (
                "Estimate airport demand pressure using seat utilization, "
                "passenger growth versus seat-capacity growth, and operational "
                "congestion. The score is a proxy, not actual unserved passenger "
                "demand or proof of insufficient capacity."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "airport_code": {
                        "type": "string",
                        "description": (
                            "Airport code, preferably ICAO, for example KSFO."
                        ),
                    },
                    "year": {
                        "type": "integer",
                        "description": (
                            "Year to analyze using BTS passenger and capacity data."
                        ),
                    },
                },
                "required": ["airport_code", "year"],
            },
        },
    },
]


tool_functions = {
    "get_flight_congestion_metrics": get_flight_congestion_metrics,
    "get_arrivals_congestion_metrics": get_arrivals_congestion_metrics,
    "get_departure_congestion_metrics": get_departure_congestion_metrics,
    "get_flight_haul_distribution": get_flight_haul_distribution,
    "rank_expansion_candidates": rank_expansion_candidates,
    "rank_regional_expansion_candidates": rank_regional_expansion_candidates,
    "estimate_unmet_demand": estimate_unmet_demand,
}