#!/bin/bash
# Red Engine Launcher — starts web server + opens browser
cd /home/j/redengine

echo "🔴 Starting Red Engine..."
echo "   Web UI: http://localhost:8080"
echo "   CLI: python3 chat.py"
echo ""

# Start web server in background
python3 web/server.py &
WEB_PID=$!
sleep 2

# Open browser
xdg-open http://localhost:8080 2>/dev/null || x-www-browser http://localhost:8080 2>/dev/null &

echo "✅ Red Engine running (web PID: $WEB_PID)"
echo "   Press Ctrl+C to stop"

# Wait for web server
wait $WEB_PID
