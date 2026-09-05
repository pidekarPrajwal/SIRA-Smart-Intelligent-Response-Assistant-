"""
tools/weather.py

Handles ONLY fetching weather data. Never touches the LLM.
"""

from typing import Dict, Any

import requests

from config import OPENWEATHER_API_KEY

WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"


def get_weather(city: str) -> Dict[str, Any]:
    """
    Return structured weather data for `city`, or an error dict.
    Never raises - callers get a dict either way.
    """
    if not city or not city.strip():
        return {"error": "No city was provided."}

    if not OPENWEATHER_API_KEY:
        return {
            "error": (
                "Weather lookups are not configured. "
                "Set the OPENWEATHER_API_KEY environment variable."
            )
        }

    try:
        response = requests.get(
            WEATHER_URL,
            params={
                "q": city,
                "appid": OPENWEATHER_API_KEY,
                "units": "metric",
            },
            timeout=10,
        )
    except requests.exceptions.RequestException as exc:
        return {"error": f"Could not reach the weather service: {exc}"}

    if response.status_code == 404:
        return {"error": f"City '{city}' was not found."}

    if response.status_code != 200:
        return {"error": f"Weather service returned status {response.status_code}."}

    try:
        data = response.json()
        return {
            "city": data["name"],
            "temperature": round(data["main"]["temp"]),
            "condition": data["weather"][0]["description"],
        }
    except (ValueError, KeyError, IndexError, TypeError):
        return {"error": "Received an invalid response from the weather service."}