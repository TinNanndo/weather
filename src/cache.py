import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

# Cache configuration
CACHE_DIR = Path.home() / ".cache" / "weather"
CACHE_FILE = CACHE_DIR / "forecast_cache.json"
CACHE_VALIDITY = timedelta(hours=1)  # Cache valid for 1 hour


def load_cache(city_name: str) -> Optional[Dict[str, Any]]:
    """
    Load cached forecast data for a city
    
    Args:
        city_name: Name of the city
        
    Returns:
        Cached forecast data or None if not found/expired
    """
    if not CACHE_FILE.exists():
        return None
    
    try:
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            cache = json.load(f)
        
        # Check if cache is for the correct city
        if cache.get('city') != city_name:
            return None
        
        # Check if cache is still valid
        cache_timestamp = datetime.fromisoformat(cache.get('timestamp', ''))
        if datetime.now() - cache_timestamp > CACHE_VALIDITY:
            return None
        
        return cache.get('data')
        
    except (json.JSONDecodeError, ValueError, KeyError) as e:
        print(f"Error reading cache: {e}")
        return None

def load_stale_cache(city_name: str) -> Optional[Dict[str, Any]]:
    """
    Load cached data even if expired (for offline fallback)
    
    Args:
        city_name: Name of the city
        
    Returns:
        Cached forecast data or None if not found
    """
    if not CACHE_FILE.exists():
        return None
    
    try:
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            cache = json.load(f)
        
        # Check if cache is for the correct city
        if cache.get('city') != city_name:
            return None
        
        # Return data even if expired (for offline use)
        return cache.get('data')
        
    except (json.JSONDecodeError, ValueError, KeyError) as e:
        print(f"Error reading stale cache: {e}")
        return None

def save_cache(city_name: str, data: Dict[str, Any]) -> bool:
    """
    Save forecast data to cache
    
    Args:
        city_name: Name of the city
        data: Forecast data to cache
        
    Returns:
        True if saved successfully, False otherwise
    """
    try:
        # Ensure cache directory exists
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        
        cache = {
            'city': city_name,
            'timestamp': datetime.now().isoformat(),
            'data': data
        }
        
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache, f, indent=2, ensure_ascii=False)
        
        return True
        
    except (IOError, OSError) as e:
        print(f"Error saving cache: {e}")
        return False


def clear_cache() -> bool:
    """
    Clear all cached data
    
    Returns:
        True if cleared successfully, False otherwise
    """
    try:
        if CACHE_FILE.exists():
            CACHE_FILE.unlink()
        return True
        
    except OSError as e:
        print(f"Error clearing cache: {e}")
        return False


def get_cache_info() -> Optional[Dict[str, Any]]:
    """
    Get information about current cache
    
    Returns:
        Dictionary with cache info or None if no cache exists
    """
    if not CACHE_FILE.exists():
        return None
    
    try:
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            cache = json.load(f)
        
        timestamp = datetime.fromisoformat(cache.get('timestamp', ''))
        age = datetime.now() - timestamp
        
        return {
            'city': cache.get('city'),
            'timestamp': timestamp,
            'age_seconds': age.total_seconds(),
            'is_valid': age <= CACHE_VALIDITY
        }
        
    except (json.JSONDecodeError, ValueError, KeyError) as e:
        print(f"Error reading cache info: {e}")
        return None
