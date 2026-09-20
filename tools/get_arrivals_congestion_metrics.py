import os
import requests
from dotenv import load_dotenv
from tools.get_arrivals import get_arrivals

load_dotenv()

API_KEY = os.getenv("FLIGHT_API_KEY")

def get_arrivals_congestion_metrics(airport_icao):
    flights = get_arrivals(airport_icao)

    if not flights:
        return {
            "airport": airport_icao,
            "total_flights": 0,
            "delayed_flights": 0,
            "delay_rate": 0,
            "average_delay": 0,
            "cancelled_flights": 0,
            "cancellation_rate": 0,
            "congestion_score": 0
        }

    total_flights = len(flights)

    delayed_flights = [
        flight for flight in flights
        if flight["arr_delayed"] is not None
        and flight["arr_delayed"] > 0
    ]

    cancelled_flights = [
        flight for flight in flights
        if flight["status"] == "cancelled"
    ]

    delay_rate = len(delayed_flights) / total_flights

    cancellation_rate = len(cancelled_flights) / total_flights

    average_delay = (
        sum(flight["arr_delayed"] for flight in delayed_flights)
        / len(delayed_flights)
        if delayed_flights
        else 0
    )

    normalized_avg_delay = min(average_delay / 60, 1)
    
    congestion_score = (
        0.7 * delay_rate +
        0.3 * normalized_avg_delay
    )

    return {
        "airport": airport_icao,
        "total_flights": total_flights,
        "delayed_flights": len(delayed_flights),
        "delay_rate": delay_rate,
        "average_delay": average_delay,
        "cancelled_flights": len(cancelled_flights),
        "cancellation_rate": cancellation_rate,
        "congestion_score": congestion_score
    }