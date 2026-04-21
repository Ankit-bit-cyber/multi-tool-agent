"""
weather.py — Current weather via OpenWeatherMap (free tier).

Falls back to a mock response when no API key is configured so the
agent still works end-to-end during development / demo mode.
"""

import httpx
from src.tools.base import tool
from config.settings import settings


def _mock_weather(city: str) -> str:
    """Return a realistic-looking mock response for dev/demo purposes."""
    return (
        f"[DEMO MODE — no OPENWEATHER_API_KEY set]\n"
        f"Weather in {city}: 28°C, partly cloudy, humidity 65%, wind 12 km/h NW."
    )


@tool(
    name="weather",
    description=(
        "Fetches the current weather for a given city. "
        "Returns temperature (°C), condition, humidity, and wind speed. "
        "Use this whenever the user asks about weather, temperature, or climate."
    ),
    param_descriptions={
        "city": "Name of the city, e.g. 'Mumbai', 'London', 'New York'"
    },
)
def weather(city: str) -> str:
    """Get current weather conditions for a city."""
    api_key = settings.openweather_api_key
    if not api_key:
        return _mock_weather(city)

    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": api_key,
        "units": "metric",
    }

    try:
        response = httpx.get(url, params=params, timeout=10.0)
        response.raise_for_status()
        data = response.json()

        temp = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        humidity = data["main"]["humidity"]
        description = data["weather"][0]["description"].capitalize()
        wind_speed = data["wind"]["speed"]
        country = data["sys"]["country"]
        city_name = data["name"]

        return (
            f"Weather in {city_name}, {country}: "
            f"{temp:.1f}°C (feels like {feels_like:.1f}°C), "
            f"{description}, "
            f"humidity {humidity}%, "
            f"wind {wind_speed} m/s."
        )

    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            return f"City '{city}' not found. Please check the spelling."
        if exc.response.status_code == 401:
            return "Invalid OpenWeatherMap API key. Check your OPENWEATHER_API_KEY."
        return f"Weather API error {exc.response.status_code}: {exc.response.text}"
    except httpx.RequestError as exc:
        return f"Network error fetching weather: {exc}"
    except Exception as exc:
        return f"Unexpected error: {exc}"