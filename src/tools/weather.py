"""Weather tool — OpenWeatherMap API wrapper."""

import os
import requests
from typing import Optional, Dict, Any
from .base import tool


class WeatherTool:
    """Weather API tool for fetching weather data."""
    
    BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
    
    @staticmethod
    @tool(
        name="weather",
        description="Get current weather for a specific city",
        input_schema={
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "City name",
                },
                "units": {
                    "type": "string",
                    "enum": ["metric", "imperial"],
                    "description": "Temperature units",
                }
            },
            "required": ["city"],
        }
    )
    def get_weather(city: str, units: str = "metric") -> Dict[str, Any]:
        """
        Fetch weather data for a city.
        
        Args:
            city: City name
            units: Temperature units (metric/imperial)
            
        Returns:
            Weather data dictionary
        """
        api_key = os.getenv("OPENWEATHER_API_KEY")
        if not api_key:
            return {"error": "OpenWeather API key not configured"}
        
        try:
            response = requests.get(
                WeatherTool.BASE_URL,
                params={"q": city, "units": units, "appid": api_key},
                timeout=5,
            )
            response.raise_for_status()
            data = response.json()
            
            return {
                "city": data.get("name"),
                "country": data.get("sys", {}).get("country"),
                "temperature": data.get("main", {}).get("temp"),
                "feels_like": data.get("main", {}).get("feels_like"),
                "description": data.get("weather", [{}])[0].get("description"),
                "humidity": data.get("main", {}).get("humidity"),
                "pressure": data.get("main", {}).get("pressure"),
            }
        except requests.exceptions.RequestException as e:
            return {"error": f"Failed to fetch weather: {str(e)}"}
