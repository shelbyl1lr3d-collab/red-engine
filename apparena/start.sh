#!/bin/bash
# AppArena Launcher - Starts the living AI app builder

echo "========================================="
echo "   AppArena - Living AI App Builder"
echo "========================================="
echo ""
echo "Starting services..."
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Python3 not found. Please install Python3."
    exit 1
fi

# Navigate to apparena directory
cd "$(dirname "$0")"

echo "Brain Status:"
python3 -c "
from brain import AppArenaBrain
brain = AppArenaBrain()
status = brain.get_alive_status()
print(f'  Alive: {status[\"alive\"]}')
print(f'  Interactions: {status[\"interactions\"]}')
print(f'  Memory Size: {status[\"memory_size\"]}')
print(f'  Personality: Enthusiasm={status[\"personality\"][\"enthusiasm\"]:.0%}, Creativity={status[\"personality\"][\"creativity\"]:.0%}')
"

echo ""
echo "Protection Status:"
python3 -c "
from extended_brain import ExtendedBrain
brain = ExtendedBrain()
status = brain.get_protection_status()
print(f'  Active: {status[\"active\"]}')
print(f'  Threats Blocked: {status[\"threats_blocked\"]}')
print(f'  Safe Mode: {status[\"safe_mode\"]}')
"

echo ""
echo "Starting web server on port 8081..."
echo ""
echo "Open in your browser:"
echo "  http://localhost:8081/dashboard.html"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Start the server
python3 -m http.server 8081
