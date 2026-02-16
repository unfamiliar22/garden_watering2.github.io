#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "=========================================="
echo "  Smart Garden Watering - Server Start"
echo "=========================================="
echo ""

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Try to find Python
PYTHON=""

if command_exists python3; then
    PYTHON="python3"
    echo -e "${GREEN}[OK]${NC} Found python3"
elif command_exists python; then
    PYTHON="python"
    echo -e "${GREEN}[OK]${NC} Found python"
elif command_exists py; then
    PYTHON="py"
    echo -e "${GREEN}[OK]${NC} Found py"
fi

if [ -z "$PYTHON" ]; then
    echo -e "${RED}[ERROR] Python not found!${NC}"
    echo ""
    echo "Please install Python 3.10 or higher:"
    echo "  - Ubuntu/Debian: sudo apt install python3 python3-venv python3-pip"
    echo "  - macOS: brew install python3"
    echo "  - Or download from: https://python.org/downloads"
    exit 1
fi

echo -e "${BLUE}[INFO]${NC} Python version:"
$PYTHON --version
echo ""

# Check Python version is 3.10+
PYTHON_VERSION=$($PYTHON -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.10"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then 
    echo -e "${YELLOW}[WARNING]${NC} Python $PYTHON_VERSION found, but Python 3.10+ is recommended"
    echo "Continuing anyway..."
    echo ""
fi

# Check if virtual environment exists
if [ -d "venv" ] && [ -f "venv/bin/python" ]; then
    echo -e "${GREEN}[OK]${NC} Virtual environment found"
    echo "Activating virtual environment..."
    source venv/bin/activate
    if [ $? -ne 0 ]; then
        echo -e "${YELLOW}[WARNING]${NC} Failed to activate, using venv Python directly..."
        PYTHON="./venv/bin/python"
    else
        PYTHON="python"
    fi
else
    echo "Virtual environment not found. Creating..."
    $PYTHON -m venv venv
    if [ $? -ne 0 ]; then
        echo -e "${RED}[ERROR] Failed to create virtual environment${NC}"
        echo "Make sure python3-venv is installed:"
        echo "  - Ubuntu/Debian: sudo apt install python3-venv"
        exit 1
    fi
    echo -e "${GREEN}[OK]${NC} Virtual environment created"
    echo ""
    echo "Installing dependencies..."
    ./venv/bin/pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo -e "${RED}[ERROR] Failed to install dependencies${NC}"
        exit 1
    fi
    echo -e "${GREEN}[OK]${NC} Dependencies installed"
    PYTHON="./venv/bin/python"
fi

echo ""
echo "=========================================="
echo "  Database Migration"
echo "=========================================="
echo ""
$PYTHON manage.py migrate
if [ $? -ne 0 ]; then
    echo -e "${RED}[ERROR] Migration failed${NC}"
    exit 1
fi
echo -e "${GREEN}[OK]${NC} Migrations applied"

echo ""
echo "=========================================="
echo "  Starting Django Server"
echo "=========================================="
echo ""
echo "Open your browser and go to:"
echo "  http://127.0.0.1:8000/"
echo ""
echo "Admin panel:"
echo "  http://127.0.0.1:8000/admin/"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop the server${NC}"
echo ""

$PYTHON manage.py runserver

if [ $? -ne 0 ]; then
    echo ""
    echo -e "${RED}[ERROR] Server stopped with error${NC}"
    exit 1
fi
