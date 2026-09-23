#!/bin/bash
# start_services.sh
# Lives on the VM at:
#   /home/azureuser/Ramakrishna/claims-SLM-Finetune/start_services.sh
# Called by run_demo.bat on the manager's Windows machine.
# Kills stale processes, then starts all 4 services in the background.

BASE=/home/azureuser/Ramakrishna/claims-SLM-Finetune
PYTHON=$BASE/../slm-env/bin/python
LOG_DIR=/tmp/motor_demo_logs

mkdir -p "$LOG_DIR"

echo "=== Motor Claims Demo — Service Startup ==="
echo "Base: $BASE"
echo ""

# ── Kill anything already running on these ports ──────────────────────────────
for PORT in 8500 8501 8502 5000; do
    PID=$(lsof -ti:$PORT 2>/dev/null)
    if [ -n "$PID" ]; then
        kill -9 $PID 2>/dev/null
        echo "[cleanup] Stopped existing process on port $PORT (PID $PID)"
    fi
done
sleep 1

# ── Terminal 1: MCP Server (port 8500) ───────────────────────────────────────
cd "$BASE/MotorTriageAgents"
nohup $PYTHON MCP/main.py > "$LOG_DIR/mcp.log" 2>&1 &
MCP_PID=$!
echo "[1/4] MCP server started (PID $MCP_PID, port 8500)"
sleep 3

# ── Terminal 2: Intake Validation Agent (port 8501) ──────────────────────────
nohup $PYTHON MotorIntakeValidationAgent/server.py > "$LOG_DIR/intake.log" 2>&1 &
INTAKE_PID=$!
echo "[2/4] Intake Validation Agent started (PID $INTAKE_PID, port 8501)"
sleep 3

# ── Terminal 3: Motor Triage Agent (port 8502) ───────────────────────────────
nohup $PYTHON MotorTriageAgent/server.py > "$LOG_DIR/triage.log" 2>&1 &
TRIAGE_PID=$!
echo "[3/4] Motor Triage Agent started (PID $TRIAGE_PID, port 8502)"
sleep 3

# ── Terminal 4: Frontend App (port 5000) ─────────────────────────────────────
cd "$BASE/motor_claims"
nohup npm run dev > "$LOG_DIR/app.log" 2>&1 &
APP_PID=$!
echo "[4/4] Frontend app started (PID $APP_PID, port 5000)"
sleep 5

# ── Health check ──────────────────────────────────────────────────────────────
echo ""
echo "=== Port check ==="
for PORT in 8500 8501 8502 5000; do
    if lsof -ti:$PORT >/dev/null 2>&1; then
        echo "  [OK]  Port $PORT is listening"
    else
        echo "  [!!]  Port $PORT is NOT listening — check $LOG_DIR/*.log"
    fi
done

echo ""
echo "Logs: $LOG_DIR/"
echo "Done. Port forwarding will connect now."
