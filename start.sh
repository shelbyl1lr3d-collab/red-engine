#!/bin/bash
# Red Engine V2 — Start All Services
# ============================================

echo "============================================"
echo "  RED ENGINE V2 — STARTING ALL SYSTEMS"
echo "============================================"
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 1. Verify .env exists
if [ ! -f .env ]; then
    echo "  [WARN] No .env file found. Copying from template..."
    cp .env.template .env
    echo "         Edit .env with your API keys before using exchange features."
fi

# 2. Load env
set -a
source .env 2>/dev/null || true
set +a

# 3. Start Web UI
echo "  [1/2] Starting Web UI on port 8080..."
kill $(lsof -ti:8080) 2>/dev/null || true
nohup python3 "$SCRIPT_DIR/web/server.py" > /tmp/redengine_web.log 2>&1 &
WEB_PID=$!
echo "         Web UI PID: $WEB_PID"

# 4. Start auto tournament (optional)
echo "  [2/2] Starting auto tournament (5min rounds)..."
nohup python3 "$SCRIPT_DIR/main.py" tournament auto 300 > /tmp/redengine_tournament.log 2>&1 &
TOURNAMENT_PID=$!
echo "         Tournament PID: $TOURNAMENT_PID"

sleep 1

echo ""
echo "============================================"
echo "  RED ENGINE V2 — READY"
echo "  Web UI:   http://localhost:8080"
echo "  Legacy:   http://localhost:1880 (Node-RED)"
echo "============================================"
echo ""
echo "Quick commands:"
echo "  python3 main.py status            — System overview"
echo "  python3 main.py chat Red 'hello'  — Chat with AI family"
echo "  python3 main.py reskin            — Generate a reskinned game"
echo "  python3 main.py forge 5           — Generate 5 games in batch"
echo "  python3 main.py tournament        — Run tournament round"
echo "  python3 main.py weekly            — Weekly report"
echo "  python3 main.py milestone_check   — Check $1B progress"
echo ""
echo "PID files: Web=$WEB_PID Tournament=$TOURNAMENT_PID"
