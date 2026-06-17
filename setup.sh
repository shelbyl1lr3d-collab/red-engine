#!/bin/bash

# Simple setup script for Red Engine V2 Desktop Application

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_color() {
    echo -e "${$1}${$2}${NC}"
}

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    print_color $RED "ERROR: Python 3 is not installed. Please install Python 3 and try again."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
if [[ "$PYTHON_VERSION" < "3.7" ]]; then
    print_color $YELLOW "WARNING: Python $PYTHON_VERSION is installed. Python 3.7 or higher is recommended."
fi

# Check if the application file exists
if [ ! -f "red_engine_desktop.py" ]; then
    print_color $RED "ERROR: red_engine_desktop.py not found in the current directory."
    print_color $YELLOW "Please ensure you are in the correct directory and the file exists."
    exit 1
fi

# Check if requirements.txt exists
if [ ! -f "requirements.txt" ]; then
    print_color $YELLOW "WARNING: requirements.txt not found. Installing dependencies..."
    # Create a simple requirements.txt if it doesn't exist
    echo "tkinter" > requirements.txt
fi

# Install dependencies
print_color $GREEN "Installing dependencies..."
pip install -r requirements.txt 2>&1 | tail -5

if [ $? -ne 0 ]; then
    print_color $RED "ERROR: Failed to install dependencies."
    exit 1
fi

# Run the application
print_color $GREEN "Starting Red Engine V2 Desktop Application..."
print_color $YELLOW "Note: If you don't see a window, try running the application manually."

# Run the application
python3 red_engine_desktop.py

# Check if the application ran successfully
if [ $? -eq 0 ]; then
    print_color $GREEN "Application closed successfully."
else
    print_color $RED "ERROR: Application failed to run."
    exit 1
fi
