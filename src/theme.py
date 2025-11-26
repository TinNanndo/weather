# src/theme.py
import tomllib
import json
from pathlib import Path

THEME_DIR = Path.home() / ".config/omarchy/current/theme"
CUSTOM_THEME = Path.home() / ".config/weather/theme.json"


def hex_to_rgb(hex_color: str) -> tuple:
    """Convert hex color to RGB tuple"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def is_light_theme(bg_color: str) -> bool:
    """Check if background color is light (luminance > 0.5)"""
    try:
        r, g, b = hex_to_rgb(bg_color)
        # Calculate relative luminance
        luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
        return luminance > 0.5
    except:
        return False


def parse_custom() -> dict | None:
    """Parse user's custom theme.json"""
    if not CUSTOM_THEME.exists():
        return None
    try:
        with open(CUSTOM_THEME) as f:
            return json.load(f)
    except Exception:
        return None


def parse_alacritty() -> dict | None:
    """Parse alacritty.toml"""
    path = THEME_DIR / "alacritty.toml"
    if not path.exists():
        return None
    try:
        with open(path, "rb") as f:
            data = tomllib.load(f)
        colors = data.get("colors", {})
        return {
            "background": colors.get("primary", {}).get("background"),
            "foreground": colors.get("primary", {}).get("foreground"),
            "black": colors.get("normal", {}).get("black"),
            "red": colors.get("normal", {}).get("red"),
            "green": colors.get("normal", {}).get("green"),
            "yellow": colors.get("normal", {}).get("yellow"),
            "blue": colors.get("normal", {}).get("blue"),
            "magenta": colors.get("normal", {}).get("magenta"),
            "cyan": colors.get("normal", {}).get("cyan"),
            "white": colors.get("normal", {}).get("white"),
        }
    except Exception:
        return None


def parse_ghostty() -> dict | None:
    """Parse ghostty.conf"""
    path = THEME_DIR / "ghostty.conf"
    if not path.exists():
        return None
    try:
        colors = {}
        with open(path) as f:
            for line in f:
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    key, val = line.split("=", 1)
                    key, val = key.strip(), val.strip()
                    if key == "background":
                        colors["background"] = val
                    elif key == "foreground":
                        colors["foreground"] = val
                    elif key.startswith("palette"):
                        idx = int(key.replace("palette", "").strip())
                        names = ["black", "red", "green", "yellow",
                                "blue", "magenta", "cyan", "white"]
                        if idx < 8:
                            colors[names[idx]] = val
        return colors if colors else None
    except Exception:
        return None


def parse_kitty() -> dict | None:
    """Parse kitty.conf"""
    path = THEME_DIR / "kitty.conf"
    if not path.exists():
        return None
    try:
        colors = {}
        color_map = {
            "color0": "black", "color1": "red", "color2": "green",
            "color3": "yellow", "color4": "blue", "color5": "magenta",
            "color6": "cyan", "color7": "white"
        }
        with open(path) as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 2:
                    key, val = parts[0], parts[1]
                    if key in ["background", "foreground"]:
                        colors[key] = val
                    elif key in color_map:
                        colors[color_map[key]] = val
        return colors if colors else None
    except Exception:
        return None


def get_omarchy_colors() -> dict:
    """Load colors with priority: omarchy -> custom -> default"""
    
    default = {
        "background": "#121212",
        "foreground": "#f5f5f5",
        "primary": "#4A8B8B",
        "accent": "#D66E36",
        "surface": "#1a1a1a",
        "error": "#B14242",
        "warning": "#F0BE66",
    }
    
    # 1. Probaj Omarchy temu prvo
    raw = parse_alacritty() or parse_ghostty() or parse_kitty()
    
    if raw:
        bg = raw.get("background", default["background"])
        fg = raw.get("foreground", default["foreground"])
        
        # Detektiraj light/dark temu
        if is_light_theme(bg):
            # Light tema - surface treba biti svjetlija od pozadine
            surface = raw.get("white", "#ffffff")
        else:
            # Dark tema - surface treba biti tamnija
            surface = raw.get("black", default["surface"])
        
        return {
            "background": bg,
            "foreground": fg,
            "primary": raw.get("blue", default["primary"]),
            "accent": raw.get("red", default["accent"]),
            "surface": surface,
            "error": raw.get("green", default["error"]),
            "warning": raw.get("yellow", default["warning"]),
        }
    
    # 2. Ako nema Omarchy, probaj custom theme.json
    custom = parse_custom()
    if custom:
        return {**default, **custom}
    
    # 3. Fallback na default
    return default
