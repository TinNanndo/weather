#!/usr/bin/env python3
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, Input, ListView, ListItem, Label
from textual.containers import Container, Vertical, ScrollableContainer
from datetime import datetime
from typing import Dict, List, Any, Optional

from api import search_cities, get_forecast, WEATHER_CODES, DAYS_SHORT
from config import get_default_city, set_default_city
from cache import load_cache, save_cache
from theme import get_omarchy_colors

def get_icon(code: int) -> str:
    """Get icon from WEATHER_CODES"""
    desc = WEATHER_CODES.get(code, "󰖐 Unknown")
    return desc.split()[0]


def get_text(code: int) -> str:
    """Get text description from WEATHER_CODES"""
    desc = WEATHER_CODES.get(code, "󰖐 Unknown")
    return " ".join(desc.split()[1:])

def generate_css() -> str:
    """Generate CSS with theme colors"""
    c = get_omarchy_colors()
    return f"""
        Screen {{
            background: {c['background']};
        }}

        Container {{
            layout: horizontal;
            height: 100%;
        }}

        Vertical {{
            background: {c['background']};
        }}

        #left_panel {{
            width: 40%;
            background: {c['background']};
        }}

        Input {{
            margin: 1 1 0 1;
            border: round {c['primary']};
            background: {c['background']};
            color: {c['foreground']};
        }}

        Input:focus {{
            border: round {c['accent']};
            border-title-color: {c['accent']};
        }}

        #cities {{
            height: 1fr;
            margin: 1;
            border: solid {c['primary']};
            background: {c['background']};
        }}

        #cities:focus {{
            border: solid {c['accent']};
            border-title-color: {c['accent']};
        }}

        ListItem {{
            background: {c['background']};
            padding: 0 1;
            text-style: none;
        }}

        ListItem > Label {{
            background: {c['background']};
            color: {c['foreground']};
            text-style: none;
        }}

        /* Mouse hover */
        ListItem:hover {{
            background: {c['accent']}40;
        }}

        ListItem:hover > Label {{
            background: {c['accent']}40;
        }}

        /* Keyboard highlight - override ALL default styles */
        ListItem.-highlight {{
            background: {c['accent']} !important;
            text-style: none !important;
        }}

        ListItem.-highlight > Label {{
            background: {c['accent']} !important;
            color: {c['background']} !important;
            text-style: none !important;
        }}

        ListView > ListItem.-highlight {{
            background: {c['accent']} !important;
        }}

        ListView > ListItem.-highlight > Label {{
            background: {c['accent']} !important;
            color: {c['background']} !important;
        }}

        ListView:focus > ListItem.-highlight {{
            background: {c['accent']} !important;
        }}

        ListView:focus > ListItem.-highlight > Label {{
            background: {c['accent']} !important;
            color: {c['background']} !important;
        }}

        Label {{
            color: {c['foreground']};
        }}

        #right {{
            width: 60%;
            border: solid {c['primary']};
            background: {c['background']};
        }}

        #right:focus {{
            border: solid {c['accent']};
            border-title-color: {c['accent']};
        }}

        #content {{
            width: 100%;
            height: 100%;
            background: {c['background']};
            color: {c['foreground']};
            content-align: center top;
        }}

        Static {{
            background: {c['background']};
        }}

        Header {{
            background: {c['background']};
            color: {c['foreground']};
        }}

        Footer {{
            background: {c['background']};
            color: {c['primary']};
        }}
    """

class WeatherTUI(App):
    """Main TUI application for weather forecasts"""

    CSS = generate_css()

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
        """Convert wind direction degrees to arrow icon"""
        if degrees < 0:
            return ""
        directions = ["󰁝", "󰁜", "󰁛", "󰁚", "󰁙", "󰁘", "󰁗", "󰁖"]
        index = int((degrees + 22.5) / 45) % 8
        return directions[index]

    def center_text(self, text: str, width: int = 50) -> str:
        """Center text within given width"""
        padding = (width - len(text)) // 2
        return " " * padding + text

    def display_forecast(self, city_info: Dict[str, Any]) -> None:
        """Display weather forecast for given city"""
        self.last_displayed_city = city_info
        content = self.query_one("#content", Static)

        cached_data = load_cache(city_info['name'])

        if cached_data:
            forecast = cached_data
        else:
            content.update(f"󰦖 Fetching forecast for {city_info['name']}...")
            forecast = get_forecast(city_info['lat'], city_info['lon'])

            if not forecast:
                content.update("󰅜 Error fetching forecast")
                return

            save_cache(city_info['name'], forecast)

        current = forecast['current']
        hourly = forecast['hourly']
        daily = forecast['daily']

        temp = current['temperature_2m']
        code = current['weather_code']
        icon = get_icon(code)
        desc = get_text(code)

        W = 60

        lines = []

        # === HEADER ===
        lines.append("")
        lines.append(self.center_text(f"{city_info['name']}, {city_info['country']}", W))
        lines.append("")
        lines.append(self.center_text(icon, W))
        lines.append(self.center_text(f"{int(temp)}°C", W))
        lines.append(self.center_text(desc, W))
        lines.append("")
        lines.append(self.center_text("─" * 60, W))

        # === HOURLY FORECAST ===
        lines.append("")
        lines.append(self.center_text("TODAY", W))
        lines.append("")

        current_hour = datetime.now().hour

        hours, icons, temps = [], [], []
        for i in range(current_hour, min(current_hour + 8, len(hourly['time']))):
            h_temp = hourly['temperature_2m'][i]
            h_code = hourly['weather_code'][i]
            h_icon = get_icon(h_code)
            dt = datetime.strptime(hourly['time'][i], "%Y-%m-%dT%H:%M")
            hours.append(dt.strftime("%H:%M"))
            icons.append(h_icon)
            temps.append(f"{int(h_temp)}°C")

        row_hours = "   ".join(f"{h:>5}" for h in hours)
        row_icons = "   ".join(f"{i:>5}" for i in icons)
        row_temps = "   ".join(f"{t:>5}" for t in temps)

        lines.append(self.center_text(row_hours, W))
        lines.append(self.center_text(row_icons, W))
        lines.append(self.center_text(row_temps, W))

        lines.append("")
        lines.append(self.center_text("─" * 60, W))

        # === DAILY FORECAST ===
        lines.append("")
        lines.append(self.center_text("NEXT 5 DAYS", W))
        lines.append("")

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

                col1 = f"{day} {date}"
                col2 = f"{d_icon}"
                col3 = f"{int(d_min):>2}°C - {int(d_max):>2}°C"
                col4 = f"{d_text}"

                line = f"    {col1:<12} {col2}  {col3:<15} {col4:<15}"
                lines.append(self.center_text(line, W))

        lines.append("")
        lines.append(self.center_text("─" * 60, W))

        # === DETAILS ===
        lines.append("")
        lines.append(self.center_text("DETAILS", W))
        lines.append("")

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

        def detail_line(icon, label, value):
            total_width = 40
            dots = "·" * (total_width - len(label) - len(str(value)) - 4)
            return f"  {icon}  {label} {dots} {value}"

        lines.append(self.center_text(detail_line("󰖎", "Humidity", f"{humidity}%"), W))
        lines.append(self.center_text(detail_line("󰔏", "Feels like", f"{int(feels_like)}°C"), W))
        lines.append(self.center_text(detail_line("󰖝", "Wind", f"{wind_speed} km/h {wind_icon}"), W))
        lines.append(self.center_text(detail_line("󰠕", "Pressure", f"{int(pressure)} hPa"), W))
        lines.append(self.center_text(detail_line("󰖙", "UV Index", f"{int(uv_index)}"), W))
        lines.append(self.center_text(detail_line("󰖜", "Sunrise", sunrise), W))
        lines.append(self.center_text(detail_line("󰖛", "Sunset", sunset), W))
        lines.append("")

        content.update("\n".join(lines))

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
            with ScrollableContainer(id="right", can_focus=True):
                yield Static("", id="content")
        yield Footer()


def main():
    """Entry point for the TUI application"""
    app = WeatherTUI()
    app.run()


if __name__ == "__main__":
    main()
