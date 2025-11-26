import requests
from typing import Dict, List, Optional

# API Configuration
GEOCODING_BASE_URL = "https://geocoding-api.open-meteo.com/v1"
FORECAST_BASE_URL = "https://api.open-meteo.com/v1/forecast"
DEFAULT_TIMEOUT = 10

# Weather condition codes (WMO codes) - Nerd Font icons
WEATHER_CODES = {
    0: "󰖙 Clear",
    1: "󰖙 Mainly clear",
    2: "󰖖 Partly cloudy",
    3: "󰖐 Overcast",
    45: "󰖑 Foggy",
    48: "󰖑 Fog",
    51: "󰖗 Light drizzle",
    53: "󰖗 Drizzle",
    55: "󰖗 Dense drizzle",
    61: "󰖛 Light rain",
    63: "󰖛 Rain",
    65: "󰖚 Heavy rain",
    66: "󰖞 Freezing rain",
    67: "󰖞 Freezing rain",
    71: "󰖜 Light snow",
    73: "󰖜 Snow",
    75: "󰖝 Heavy snow",
    77: "󰖜 Snow grains",
    80: "󰖗 Light showers",
    81: "󰖛 Showers",
    82: "󰖚 Heavy showers",
    85: "󰖘 Snow showers",
    86: "󰖝 Heavy snow",
    95: "󰖓 Thunderstorm",
    96: "󰖓 Thunderstorm",
    99: "󰖓 Thunderstorm"
}

DAYS_SHORT = {
    "Monday": "Mon", "Tuesday": "Tue", "Wednesday": "Wed",
    "Thursday": "Thu", "Friday": "Fri", "Saturday": "Sat", "Sunday": "Sun"
}

def get_city_coordinates(city_name: str, language: str = "en") -> Optional[Dict]:
    """
    Get coordinates for a city name

    Args:
        city_name: Name of the city to search
        language: Language code for results (default: "en")

    Returns:
        Dictionary with city info or None if not found
    """
    url = f"{GEOCODING_BASE_URL}/search"
    params = {
        "name": city_name,
        "language": language,
        "count": 1
    }

    try:
        response = requests.get(url, params=params, timeout=DEFAULT_TIMEOUT)
        response.raise_for_status()
        data = response.json()

        if "results" in data and len(data["results"]) > 0:
            result = data["results"][0]
            return {
                "name": result["name"],
                "lat": result["latitude"],
                "lon": result["longitude"],
                "country": result.get("country", ""),
                "population": result.get("population", 0)
            }

        return None

    except requests.RequestException as e:
        print(f"Error fetching coordinates: {e}")
        return None


def search_cities(query: str, max_results: int = 20, language: str = "en") -> List[Dict]:
    """
    Search for cities matching query

    Args:
        query: Search query
        max_results: Maximum number of results (default: 20)
        language: Language code for results (default: "en")

    Returns:
        List of matching cities
    """
    url = f"{GEOCODING_BASE_URL}/search"
    params = {
        "name": query,
        "count": max_results,
        "language": language
    }

    try:
        response = requests.get(url, params=params, timeout=DEFAULT_TIMEOUT)
        response.raise_for_status()
        data = response.json()

        if "results" not in data:
            return []

        cities = []
        for city in data["results"]:
            cities.append({
                "name": city["name"],
                "lat": city["latitude"],
                "lon": city["longitude"],
                "country": city.get("country", ""),
                "admin": city.get("admin1", "")
            })

        return cities

    except requests.RequestException as e:
        print(f"Error searching cities: {e}")
        return []


def get_forecast(lat: float, lon: float) -> Optional[Dict]:
    """
    Get weather forecast for coordinates

    Args:
        lat: Latitude
        lon: Longitude

    Returns:
        Forecast data dictionary or None if failed
    """
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": ",".join([
            "temperature_2m",
            "relative_humidity_2m",
            "apparent_temperature",
            "weather_code",
            "wind_speed_10m",
            "wind_direction_10m",
            "pressure_msl"
        ]),
        "hourly": ",".join([
            "temperature_2m",
            "weather_code"
        ]),
        "daily": ",".join([
            "temperature_2m_max",
            "temperature_2m_min",
            "weather_code",
            "uv_index_max",
            "sunrise",
            "sunset"
        ]),
        "timezone": "auto"
    }

    try:
        response = requests.get(FORECAST_BASE_URL, params=params, timeout=DEFAULT_TIMEOUT)
        response.raise_for_status()
        return response.json()

    except requests.RequestException as e:
        print(f"Error fetching forecast: {e}")
        return None
