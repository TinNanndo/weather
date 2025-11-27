#!/bin/bash

if pgrep -f "python3.*tui.py" > /dev/null; then
    pkill -f "python3.*tui.py"
else
    # Detect terminal
    if command -v foot &> /dev/null; then
        foot --app-id=weather-tui python3 ~/.config/weather/src/tui.py &
    elif command -v alacritty &> /dev/null; then
        alacritty --class weather-tui -e python3 ~/.config/weather/src/tui.py &
    elif command -v kitty &> /dev/null; then
        kitty --class weather-tui python3 ~/.config/weather/src/tui.py &
    elif command -v ghostty &> /dev/null; then
        ghostty -e bash -c 'printf "\033]0;WeatherTUI\007"; python3 ~/.config/weather/src/tui.py' &
    else
        python3 ~/.config/weather/src/tui.py &
    fi
    
    sleep 0.3
    
    if command -v hyprctl &> /dev/null; then
        hyprctl dispatch focuswindow "title:WeatherTUI"
        hyprctl dispatch setfloating
        hyprctl dispatch resizeactive exact 70% 80%
        hyprctl dispatch centerwindow
    fi
fi
