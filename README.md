# Weather TUI

A minimalist terminal weather application for Hyprland/Waybar.



## Light Theme

![Screenshot(light)](screenshot(light).png)

## Dark Theme

![Screenshot(dark)](screenshot(dark).png)

## Features

- Current weather with 8-hour and 5-day forecast
- City search with smart caching (10min)
- Automatic Omarchy theme detection
- Waybar integration with hover tooltip
- Nerd Font icons

## Installation
```bash
cd ~/.config
git clone https://github.com/TinNanndo/weather
cd weather
pip install -r requirements.txt
```

## Usage
```bash
python3 src/tui.py
```

| Key | Action |
|-----|--------|
| `↑` `↓` | Navigate cities |
| `Enter` | Select city |
| `s` | Set as default |
| `q` | Quit |

## Waybar

Add to `~/.config/waybar/config.jsonc`:
```jsonc
"custom/weather": {
    "exec": "python3 ~/.config/weather/scripts/weather_waybar.py",
    "return-type": "json",
    "interval": 900,
    "on-click": "~/.config/weather/scripts/launch_tui.sh"
}
```

**Note:** Add a comma before/after if needed for valid JSON.

## Hyprland

Window floating is handled automatically by the launch script. No manual configuration needed!

(Optional) If you prefer manual window rules, add to `~/.config/hypr/hyprland.conf`:
```conf
windowrulev2 = float, class:(weather-tui)
windowrulev2 = size 70% 80%, class:(weather-tui)
windowrulev2 = center, class:(weather-tui)
```
```
```

## Theming

### Automatic (Omarchy)

The app automatically detects your Omarchy theme from:
- `~/.config/omarchy/current/theme/alacritty.toml`
- `~/.config/omarchy/current/theme/ghostty.conf`
- `~/.config/omarchy/current/theme/kitty.conf`

### Custom Theme

Create `~/.config/weather/theme.json`:
```json
{
    "background": "#1a1b26",
    "foreground": "#c0caf5",
    "primary": "#7aa2f7",
    "accent": "#f7768e",
    "surface": "#24283b"
}
```

Custom theme overrides Omarchy detection.

## API

Uses [Open-Meteo](https://open-meteo.com/) - free, no API key required.

## Credits

- [Open-Meteo](https://open-meteo.com/) - Weather data
- [Textual](https://github.com/Textualize/textual) - TUI framework
- [Nerd Fonts](https://www.nerdfonts.com/) - Icons
