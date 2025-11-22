#!/usr/bin/env python3
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, Input, ListView, ListItem, Label
from textual.containers import Container, Vertical, ScrollableContainer
from datetime import datetime
from typing import Dict, List, Any, Optional

from api import search_cities, get_forecast, WEATHER_CODES
from config import get_default_city, set_default_city
from cache import load_cache, save_cache


class WeatherTUI(App):
    """Main TUI application for weather forecasts"""
    
    CSS = """
        Screen {
            background: $background;
        }

        Container {
            layout: horizontal;
            height: 100%;
        }

        Vertical {
            background: $background;
        }

        #left_panel {
            width: 40%;
        }

        Input {
            margin: 1 1 0 1;
            border: round $primary;
            background: $surface;
            color: $text;
        }

        Input:focus {
            border: round $accent;
            border-title-color: $accent;
        }

        #cities {
            height: 1fr;
            margin: 1;
            border: solid $primary;
            background: $surface;
        }

        #cities:focus {
            border: solid $accent;
            border-title-color: $accent;
        }

        ListItem {
            background: $surface;
        }

        ListItem:hover {
            background: $surface-lighten-1;
        }

        Label {
            color: $text;
        }

        #right {
            width: 60%;
            border: solid $primary;
            background: $surface;
        }

        #content {
            width: 100%;
            height: 100%;
            background: transparent;
            color: $text;
            content-align: center top;
        }

        Static {
            background: $surface;
        }

        Header {
            background: $background;
            color: $text;
        }

        Footer {
            background: $background;
            color: $text-muted;
        }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("escape", "quit", "Quit"),
        ("s", "set_default", "Set as default"),
    ]

    def __init__(self):
        super().__init__()
        self.current_cities: List[Dict[str, Any]] = []
        self.search_timer: Optional[Any] = None
        self.last_displayed_city: Optional[Dict[str, Any]] = None

    def on_mount(self) -> None:
        """Initialize the application when mounted"""
        self.query_one("#search", Input).border_title = "Search"
        self.query_one("#cities", ListView).border_title = "Cities"
        self.query_one("#right", ScrollableContainer).border_title = "Forecast"

        # Load and display default city
        city_info = get_default_city()
        if city_info:
            self.display_forecast(city_info)

    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle search input changes with debouncing"""
        text = event.value.strip()

        if self.search_timer is not None:
            self.search_timer.stop()

        self.search_timer = self.set_timer(0.5, lambda: self.search(text))

    def search(self, query: str) -> None:
        """Search for cities matching query"""
        cities_list = self.query_one("#cities", ListView)
        cities_list.clear()

        if len(query) < 2:
            return

        cities_list.append(ListItem(Label("Searching...")))
        results = search_cities(query)
        cities_list.clear()

        self.current_cities = results

        for city in results:
            display = f"{city['name']}, {city['country']}"
            cities_list.append(ListItem(Label(display)))

    def wind_direction_icon(self, degrees: float) -> str:
        """
        Convert wind direction degrees to arrow icon
        
        Args:
            degrees: Wind direction in degrees (0-360)
            
        Returns:
            Nerd Font arrow icon
        """
        if degrees < 0:
            return ""
        
        # N, NE, E, SE, S, SW, W, NW
        directions = ["󰁝", "󰁜", "󰁛", "󰁚", "󰁙", "󰁘", "󰁗", "󰁖"]
        index = int((degrees + 22.5) / 45) % 8
        return directions[index]

    def center_text(self, text: str, width: int = 50) -> str:
        """
        Center text within given width
        
        Args:
            text: Text to center
            width: Total width for centering
            
        Returns:
            Centered text with padding
        """
        padding = (width - len(text)) // 2
        return " " * padding + text

    def display_forecast(self, city_info: Dict[str, Any]) -> None:
        """
        Display weather forecast for given city
        
        Args:
            city_info: Dictionary with city data (name, lat, lon, country)
        """
        self.last_displayed_city = city_info
        content = self.query_one("#content", Static)

        # Try to load from cache first
        cached_data = load_cache(city_info['name'])

        if cached_data:
            forecast = cached_data
        else:
            content.update(f"🔄 Fetching forecast for {city_info['name']}...")
            forecast = get_forecast(city_info['lat'], city_info['lon'])

            if not forecast:
                content.update("❌ Error fetching forecast")
                return

            save_cache(city_info['name'], forecast)

        # Extract data
        current = forecast['current']
        hourly = forecast['hourly']
        daily = forecast['daily']

        temp = current['temperature_2m']
        code = current['weather_code']
        description = WEATHER_CODES.get(code, "❓ Unknown")
        emoji = description.split()[0]
        desc_text = " ".join(description.split()[1:])

        # Build display text
        text = "\n"
        
        # === HERO SECTION ===
        text += self.center_text(f"{city_info['name']}, {city_info['country']}", 50) + "\n\n"
        text += self.center_text(emoji, 50) + "\n\n"
        text += self.center_text(f"{int(temp)}°C", 50) + "\n\n"
        text += self.center_text(desc_text, 50) + "\n\n"
        text += self.center_text("─" * 50, 50) + "\n\n"

        # === HOURLY FORECAST ===
        text += self.center_text("NEXT 8 HOURS", 50) + "\n\n"

        hours, emojis, temps = [], [], []
        for i in range(8):
            time_str = hourly['time'][i]
            temp_h = hourly['temperature_2m'][i]
            code_h = hourly['weather_code'][i]

            dt = datetime.strptime(time_str, "%Y-%m-%dT%H:%M")
            hour = dt.strftime("%H:%M")

            desc_h = WEATHER_CODES.get(code_h, "❓")
            emoji_h = desc_h.split()[0]

            hours.append(hour)
            emojis.append(emoji_h)
            temps.append(f"{int(temp_h)}°C")

        row_hours = "  ".join(f"{h:>5}" for h in hours)
        row_emoji = "  ".join(f"{e:>5}" for e in emojis)
        row_temp = "  ".join(f"{t:>5}" for t in temps)

        text += self.center_text(row_hours, 50) + "\n"
        text += self.center_text(row_emoji, 50) + "\n"
        text += self.center_text(row_temp, 50) + "\n\n"
        text += self.center_text("─" * 50, 50) + "\n\n"

        # === DAILY FORECAST ===
        text += self.center_text("NEXT 5 DAYS", 50) + "\n\n"

        days_short = {
            "Monday": "Mon", "Tuesday": "Tue", "Wednesday": "Wed",
            "Thursday": "Thu", "Friday": "Fri", "Saturday": "Sat", "Sunday": "Sun"
        }

        for i in range(1, 6):  # Skip today (0)
            date_str = daily['time'][i]
            t_max = daily['temperature_2m_max'][i]
            t_min = daily['temperature_2m_min'][i]
            code_d = daily['weather_code'][i]

            dt = datetime.strptime(date_str, "%Y-%m-%d")
            day_name = dt.strftime("%A")
            date_fmt = dt.strftime("%d.%m.")

            day_short = days_short.get(day_name, day_name)
            desc_d = WEATHER_CODES.get(code_d, "❓")
            emoji_d = desc_d.split()[0]

            line = f"{day_short:<4} {date_fmt:<8} {emoji_d:>3}  {int(t_min):>3}°C - {int(t_max):>3}°C"
            text += self.center_text(line, 50) + "\n"

        text += "\n" + self.center_text("─" * 50, 50) + "\n\n"

        # === DETAILS ===
        text += self.center_text("DETAILS", 50) + "\n\n"

        humidity = current.get('relative_humidity_2m', 'N/A')
        feels_like = current.get('apparent_temperature', temp)
        wind_speed = current.get('wind_speed_10m', 0)
        wind_dir = current.get('wind_direction_10m', 0)
        pressure = current.get('pressure_msl', 0)

        uv_index = daily.get('uv_index_max', [0])[0]
        sunrise_str = daily.get('sunrise', [''])[0]
        sunset_str = daily.get('sunset', [''])[0]

        if sunrise_str and sunset_str:
            sunrise_dt = datetime.strptime(sunrise_str, "%Y-%m-%dT%H:%M")
            sunset_dt = datetime.strptime(sunset_str, "%Y-%m-%dT%H:%M")
            sunrise = sunrise_dt.strftime("%H:%M")
            sunset = sunset_dt.strftime("%H:%M")
        else:
            sunrise = "N/A"
            sunset = "N/A"

        wind_icon = self.wind_direction_icon(wind_dir)

        text += self.center_text(f"󰖎  Humidity         {humidity}%", 50) + "\n"
        text += self.center_text(f"  Feels like       {int(feels_like)}°C", 50) + "\n"
        text += self.center_text(f"󰈐  Wind             {wind_speed} km/h {wind_icon}", 50) + "\n"
        text += self.center_text(f"  Pressure         {int(pressure)} hPa", 50) + "\n"
        text += self.center_text(f"󰖙  UV Index         {int(uv_index)}", 50) + "\n"
        text += self.center_text(f"󰖜  Sunrise          {sunrise}", 50) + "\n"
        text += self.center_text(f"󰖛  Sunset           {sunset}", 50) + "\n\n"

        content.update(text)

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle city selection from list"""
        cities_list = self.query_one("#cities", ListView)
        index = cities_list.index

        if index < len(self.current_cities):
            city_info = self.current_cities[index]
            self.display_forecast(city_info)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle Enter key in search field"""
        if len(self.current_cities) > 0:
            city_info = self.current_cities[0]
            self.display_forecast(city_info)

            cities_list = self.query_one("#cities", ListView)
            cities_list.focus()

    def action_set_default(self) -> None:
        """Set currently displayed city as default"""
        if self.last_displayed_city:
            city_info = self.last_displayed_city
        
            # Spremi u config
            if set_default_city(city_info):
                self.sub_title = f"✓ {city_info['name']}, {city_info['country']} set as default"
            else:
                self.sub_title = f"✗ Failed to save {city_info['name']}"
        
            self.set_timer(3, lambda: setattr(self, 'sub_title', ''))

    def compose(self) -> ComposeResult:
        """Compose the UI layout"""
        yield Header()
        with Container():
            with Vertical(id="left_panel"):
                yield Input(placeholder="Enter city name...", id="search")
                yield ListView(id="cities")
            with ScrollableContainer(id="right"):
                yield Static("", id="content")
        yield Footer()


def main():
    """Entry point for the TUI application"""
    app = WeatherTUI()
    app.run()


if __name__ == "__main__":
    main()
