import json
from pathlib import Path
from typing import Dict, Any, Optional

# Configuration paths
CONFIG_DIR = Path.home() / ".config" / "weather"
CONFIG_FILE = CONFIG_DIR / "config.json"

# Default configuration
DEFAULT_CONFIG = {
    "default_city": {
        "name": "Zagreb",
        "lat": 45.815,
        "lon": 15.982,
        "country": "Croatia"
    }
}


def load_config() -> Dict[str, Any]:
    """
    Load configuration from file or return defaults
    
    Returns:
        Configuration dictionary
    """
    if not CONFIG_FILE.exists():
        return DEFAULT_CONFIG.copy()
    
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Migrate old format (string) to new format (dict)
        if "default_city" in config and isinstance(config["default_city"], str):
            config["default_city"] = {
                "name": config["default_city"],
                "lat": 45.815,
                "lon": 15.982,
                "country": "Croatia"
            }
            save_config(config)
        
        return config
        
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading config: {e}")
        return DEFAULT_CONFIG.copy()


def save_config(config: Dict[str, Any]) -> bool:
    """
    Save configuration to file
    
    Args:
        config: Configuration dictionary to save
        
    Returns:
        True if saved successfully, False otherwise
    """
    try:
        # Ensure config directory exists
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        return True
        
    except (IOError, OSError) as e:
        print(f"Error saving config: {e}")
        return False


def set_default_city(city_info: Dict[str, Any]) -> bool:
    config = load_config()
    
    config["default_city"] = {
        "name": city_info.get("name", city_info.get("ime", "Unknown")),
        "lat": city_info["lat"],
        "lon": city_info["lon"],
        "country": city_info.get("country", city_info.get("drzava", "Unknown"))
    }
    
    return save_config(config)


def get_default_city() -> Dict[str, Any]:
    """
    Get the default city information
    
    Returns:
        Dictionary with city data (name, lat, lon, country)
    """
    config = load_config()
    
    default_city = config.get("default_city")
    
    # Fallback to default if not set
    if not default_city:
        return DEFAULT_CONFIG["default_city"].copy()
    
    # Ensure all required fields exist
    return {
        "name": default_city.get("name", "Zagreb"),
        "lat": default_city.get("lat", 45.815),
        "lon": default_city.get("lon", 15.982),
        "country": default_city.get("country", "Croatia")
    }


def reset_config() -> bool:
    """
    Reset configuration to defaults
    
    Returns:
        True if reset successfully, False otherwise
    """
    return save_config(DEFAULT_CONFIG.copy())


def get_config_path() -> Path:
    """
    Get the path to the configuration file
    
    Returns:
        Path object pointing to config file
    """
    return CONFIG_FILE
