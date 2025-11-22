#!/usr/bin/env python3
import sys
import json
from pathlib import Path
from datetime import datetime

# Add src to path for imports
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
sys.path.insert(0, str(PROJECT_DIR / "src"))

from config import get_default_city
from api import get_forecast, WEATHER_CODES
from cache import load_cache, save_cache

def format_tooltip(city_name, forecast_data):
    """Format tooltip with hourly and daily forecast"""
    current = forecast_data["current"]
    hourly = forecast_data["hourly"]
    daily = forecast_data["daily"]
    
    temp = current["temperature_2m"]
    code = current["weather_code"]
    description = WEATHER_CODES.get(code, "❓ Unknown")
    
    # Start tooltip
    tooltip = f"{city_name}: {temp}°C, {description}\n\n"
    
    # Hourly forecast (next 6 hours)
    tooltip += "─" * 30 + "\nToday:\n"
    current_hour = datetime.now().hour
    
    for i in range(current_hour, min(current_hour + 6, 24)):
        time_str = hourly["time"][i]
        dt = datetime.strptime(time_str, "%Y-%m-%dT%H:%M")
        hour = dt.strftime("%H:%M")
        temp_h = hourly["temperature_2m"][i]
        code_h = hourly["weather_code"][i]
        desc_h = WEATHER_CODES.get(code_h, "❓")
        
        tooltip += f"   {hour}   {temp_h}°C   {desc_h}\n"
    
    tooltip += "\n"
    
    # Daily forecast (next 5 days)
    tooltip += "─" * 30 + "\nNext 5 days:\n"
    
    days_short = {
        "Monday": "Mon", "Tuesday": "Tue", "Wednesday": "Wed",
        "Thursday": "Thu", "Friday": "Fri", "Saturday": "Sat", "Sunday": "Sun"
    }
    
    for i in range(1, 6):  # Skip today (0), show 1-5
        date_str = daily["time"][i]
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        day_name = dt.strftime("%A")
        day_short = days_short[day_name]
        date_fmt = dt.strftime("%d.%m.")
        
        t_max = daily["temperature_2m_max"][i]
        t_min = daily["temperature_2m_min"][i]
        code_d = daily["weather_code"][i]
        desc_d = WEATHER_CODES.get(code_d, "❓")
        
        tooltip += f"   {day_short} {date_fmt}   {t_min}°C - {t_max}°C   {desc_d}\n"
    
    return tooltip


def main():
    """Main entry point for Waybar module"""
    try:
        # Get default city
        city_info = get_default_city()
        
        # Try to load from cache first
        cached_data = load_cache(city_info["name"])
        
        if cached_data:
            forecast = cached_data
        else:
            # Fetch fresh data
            forecast = get_forecast(city_info["lat"], city_info["lon"])
            
            if not forecast:
                # No internet and no cache - show cached message
                print(json.dumps({
                    "text": f"{city_info['name']}: Offline",
                    "tooltip": "No internet connection\nUsing cached data if available",
                    "class": "offline"
                }), flush=True)
                return
            
            # Save to cache
            save_cache(city_info["name"], forecast)
        
        # Format output
        temp = forecast["current"]["temperature_2m"]
        code = forecast["current"]["weather_code"]
        description = WEATHER_CODES.get(code, "❓ Unknown")
        emoji = description.split()[0]
        
        tooltip = format_tooltip(city_info["name"], forecast)
        
        output = {
            "text": f"{city_info['name']}: {emoji} {temp}°C",
            "tooltip": tooltip,
            "class": "weather"
        }
        
        print(json.dumps(output, ensure_ascii=False), flush=True)
        
    except Exception as e:
        # Catch-all error handler - always output valid JSON
        print(json.dumps({
            "text": "Weather: Error",
            "tooltip": f"Error: {str(e)}",
            "class": "error"
        }), flush=True)


if __name__ == "__main__":
    main()
