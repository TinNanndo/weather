#!/bin/bash

# Weather TUI Installation Script
# Installs dependencies and sets up configuration

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${BLUE}→${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Check Python installation
check_python() {
    print_info "Checking Python installation..."
    
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 not found. Please install Python 3.8 or higher."
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    print_success "Python $PYTHON_VERSION found"
}

# Check pip installation
check_pip() {
    print_info "Checking pip installation..."
    
    if ! command -v pip3 &> /dev/null && ! python3 -m pip --version &> /dev/null; then
        print_error "pip not found. Please install pip."
        exit 1
    fi
    
    print_success "pip found"
}

# Install Python dependencies
install_dependencies() {
    print_info "Installing Python dependencies..."
    
    if [ -f "requirements.txt" ]; then
        python3 -m pip install --user -r requirements.txt
        print_success "Dependencies installed"
    else
        print_warning "requirements.txt not found, skipping dependency installation"
    fi
}

# Make scripts executable
setup_scripts() {
    print_info "Setting up scripts..."
    
    if [ -f "scripts/launch_tui.sh" ]; then
        chmod +x scripts/launch_tui.sh
        print_success "launch_tui.sh is now executable"
    fi
    
    if [ -f "scripts/weather_waybar.py" ]; then
        chmod +x scripts/weather_waybar.py
        print_success "weather_waybar.py is now executable"
    fi
}

# Create default configuration
create_config() {
    print_info "Setting up configuration..."
    
    if [ -f "config.json" ]; then
        print_warning "config.json already exists, skipping"
    else
        cat > config.json << 'EOF'
{
  "default_city": {
    "name": "Zagreb",
    "lat": 45.815,
    "lon": 15.982,
    "country": "Croatia"
  }
}
EOF
        print_success "Created default config.json"
    fi
}

# Create cache directory
create_cache_dir() {
    print_info "Creating cache directory..."
    
    CACHE_DIR="$HOME/.cache/weather"
    mkdir -p "$CACHE_DIR"
    print_success "Cache directory created at $CACHE_DIR"
}

# Test installation
test_installation() {
    print_info "Testing installation..."
    
    # Test if modules can be imported
    if python3 -c "import sys; sys.path.insert(0, 'src'); from api import WEATHER_CODES, DAYS_SHORT; from config import get_default_city; from cache import load_cache" 2>/dev/null; then
        print_success "All modules loaded successfully"
    else
        print_error "Module import failed. Installation may be incomplete."
        return 1
    fi
    
    # Test waybar script
    if [ -f "scripts/weather_waybar.py" ]; then
        if python3 scripts/weather_waybar.py &> /dev/null; then
            print_success "Waybar script works"
        else
            print_warning "Waybar script test failed (this is OK if no internet)"
        fi
    fi
}

# Display next steps
show_next_steps() {
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "${GREEN}Installation complete!${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "Next steps:"
    echo ""
    echo "1. Test the TUI application:"
    echo -e "   ${BLUE}python3 src/tui.py${NC}"
    echo ""
    echo "2. Add to Waybar config (~/.config/waybar/config.jsonc):"
    echo -e "   ${YELLOW}\"custom/weather\": {"
    echo "     \"exec\": \"python3 ~/.config/weather/scripts/weather_waybar.py\","
    echo "     \"return-type\": \"json\","
    echo "     \"interval\": 900,"
    echo "     \"on-click\": \"~/.config/weather/scripts/launch_tui.sh\""
    echo -e "   }${NC}"
    echo ""
    echo "3. Add Hyprland window rules (~/.config/hypr/hyprland.conf):"
    echo ""
    echo "   For Ghostty (title matching):"
    echo -e "   ${YELLOW}windowrulev2 = float, title:^(WeatherTUI)\$"
    echo "   windowrulev2 = size 70% 80%, title:^(WeatherTUI)\$"
    echo -e "   windowrulev2 = center, title:^(WeatherTUI)\$${NC}"
    echo ""
    echo "   For Alacritty/Kitty (class matching):"
    echo -e "   ${YELLOW}windowrulev2 = float, class:(weather-tui)"
    echo "   windowrulev2 = size 70% 80%, class:(weather-tui)"
    echo -e "   windowrulev2 = center, class:(weather-tui)${NC}"
    echo ""
    echo "4. Reload Waybar and Hyprland:"
    echo -e "   ${BLUE}killall waybar && waybar &${NC}"
    echo -e "   ${BLUE}hyprctl reload${NC}"
    echo ""
    echo "5. (Optional) Custom theme - create ~/.config/weather/theme.json"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

# Main installation flow
main() {
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "          Weather TUI - Installation Script"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    check_python
    check_pip
    install_dependencies
    setup_scripts
    create_config
    create_cache_dir
    
    echo ""
    
    if test_installation; then
        show_next_steps
    else
        print_error "Installation completed with errors. Please check the output above."
        exit 1
    fi
}

# Run main installation
main
