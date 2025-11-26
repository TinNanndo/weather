#!/usr/bin/env python3
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from api import get_forecast
from config import get_default_city
from cache import load_cache, save_cache

# Nerd Font Material Design weather icons
WEATHER_ICONS = {
    0: "󰖙",   # Clear sky - sunny
    1: "󰖙",   # Mainly clear - sunny
    2: "󰖖",   # Partly cloudy
    3: "󰖐",   # Overcast - cloudy
    45: "󰖑",  # Foggy
    48: "󰖑",  # Fog
    51: "󰖗",  # Light drizzle
    53: "󰖗",  # Moderate drizzle
    55: "󰖗",  # Dense drizzle
    61: "󰖛",  # Slight rain
    63: "󰖛",  # Moderate rain
    65: "󰖚",  # Heavy rain - pouring
    66: "󰖞",  # Freezing rain
    67: "󰖞",  # Heavy freezing rain
    71: "󰖜",  # Slight snow
    73: "󰖜",  # Moderate snow
    75: "󰖝",  # Heavy snow
    77: "󰖜",  # Snow grains
    80: "󰖗",  # Slight rain showers
    81: "󰖛",  # Moderate rain showers
    82: "󰖚",  # Violent rain showers
    85: "󰖘",  # Slight snow showers
    86: "󰖝",  # Heavy snow showers
    95: "󰖓",  # Thunderstorm
    96: "󰖓",  # Thunderstorm with hail
    99: "󰖓",  # Thunderstorm with heavy hail
}

WEATHER_TEXT = {
    0: "Clear",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Foggy",
    48: "Fog",
    51: "Light drizzle",
    53: "Drizzle",
    55: "Dense drizzle",
    61: "Light rain",
    63: "Rain",
    65: "Heavy rain",
    66: "Freezing rain",
    67: "Freezing rain",
    71: "Light snow",
    73: "Snow",
    75: "Heavy snow",
    77: "Snow grains",
    80: "Light showers",
    81: "Showers",
    82: "Heavy showers",
    85: "Snow showers",
    86: "Heavy snow",
    95: "Thunderstorm",
    96: "Thunderstorm",
    99: "Thunderstorm",
}

DAYS_SHORT = {
    "Monday": "Mon", "Tuesday": "Tue", "Wednesday": "Wed",
    "Thursday": "Thu", "Friday": "Fri", "Saturday": "Sat", "Sunday": "Sun"
}


def get_icon(code: int) -> str:
    return WEATHER_ICONS.get(code, "󰖐")


def get_text(code: int) -> str:
    return WEATHER_TEXT.get(code, "Unknown")


def format_tooltip(city: dict, forecast: dict) -> str:
    current = forecast['current']
    hourly = forecast['hourly']
    daily = forecast['daily']

    temp = current['temperature_2m']
    code = current['weather_code']
    icon = get_icon(code)
    desc = get_text(code)

    lines = []
    
    # Header
    lines.append(f"{city['name']}: {temp}°C, {icon} {desc}")
    lines.append("─" * 40)
    
    # Today's hourly
    lines.append("Today:")
    current_hour = datetime.now().hour
    for i in range(current_hour, min(current_hour + 6, 24)):
        if i < len(hourly['time']):
            h_temp = hourly['temperature_2m'][i]
            h_code = hourly['weather_code'][i]
            h_icon = get_icon(h_code)
            h_text = get_text(h_code)
            dt = datetime.strptime(hourly['time'][i], "%Y-%m-%dT%H:%M")
            lines.append(f"    {dt.strftime('%H:%M')}   {h_temp:>5.1f}°C   {h_icon}  {h_text}")
    
    lines.append("─" * 40)
    
    # Next 5 days
    lines.append("Next 5 days:")
    for i in range(1, 6):
        if i < len(daily['time']):
            d_min = daily['temperature_2m_min'][i]
            d_max = daily['temperature_2m_max'][i]
            d_code = daily['weather_code'][i]
            d_icon = get_icon(d_code)
            d_text = get_text(d_code)
            dt = datetime.strptime(daily['time'][i], "%Y-%m-%d")
            day = DAYS_SHORT.get(dt.strftime("%A"), dt.strftime("%a"))
            date = dt.strftime("%d.%m.")
            lines.append(f"    {day} {date}   {d_min:>4.1f}°C - {d_max:>4.1f}°C   {d_icon}  {d_text}")

    return "\n".join(lines)


def main():
    city = get_default_city()
    
    if not city:
        output = {
            "text": "󰖐 --°C",
            "tooltip": "No city configured",
            "class": "weather"
        }
        print(json.dumps(output))
        return

    forecast = load_cache(city['name'])
    
    if not forecast:
        forecast = get_forecast(city['lat'], city['lon'])
        if forecast:
            save_cache(city['name'], forecast)

    if not forecast:
        output = {
            "text": "󰖐 --°C",
            "tooltip": "Failed to fetch weather",
            "class": "weather-error"
        }
        print(json.dumps(output))
        return

    current = forecast['current']
    temp = current['temperature_2m']
    code = current['weather_code']
    icon = get_icon(code)

    output = {
        "text": f"{city['name']}: {icon} {temp:.1f}°C",
        "tooltip": format_tooltip(city, forecast),
        "class": "weather"
    }
    
    print(json.dumps(output))


if __name__ == "__main__":
    main()
