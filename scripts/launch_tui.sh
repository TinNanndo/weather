#!/bin/bash

# Check if weather-tui is already running
if pgrep -f "class:weather-tui" > /dev/null || pgrep -f "python3.*tui.py" > /dev/null; then
    # Already running - kill it
    pkill -f "python3.*tui.py"
else
    # Not running - launch it
    # Detect terminal
    if command -v ghostty &> /dev/null; then
        ghostty --class=weather-tui -e python3 ~/.config/weather/src/tui.py
    elif command -v alacritty &> /dev/null; then
        alacritty --class weather-tui -e python3 ~/.config/weather/src/tui.py
    elif command -v kitty &> /dev/null; then
        kitty --class weather-tui python3 ~/.config/weather/src/tui.py
    else
        # Fallback
        python3 ~/.config/weather/src/tui.py
    fi
fi
