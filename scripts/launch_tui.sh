#!/bin/bash
# Launch Weather TUI in floating window

# Detect terminal
if command -v alacritty &> /dev/null; then
    alacritty --class weather-tui -e python3 ~/.config/weather/src/tui.py
elif command -v kitty &> /dev/null; then
    kitty --class weather-tui python3 ~/.config/weather/src/tui.py
elif command -v ghostty &> /dev/null; then
    ghostty --class weather-tui -e python3 ~/.config/weather/src/tui.py
else
    # Fallback to default terminal
    python3 ~/.config/weather/src/tui.py
fi
