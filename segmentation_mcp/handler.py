#!/bin/bash

# ============================================================
# Motor Triage Demo Launcher
# ============================================================

BASE_DIR="/home/azureuser/Ramakrishna/claims-SLM-Finetune"
AGENTS_DIR="$BASE_DIR/MotorTriageAgents"
VENV="$BASE_DIR/slm-env/bin/python"

LOG_DIR="$BASE_DIR/demo_logs"

mkdir -p "$LOG_DIR"

echo ""
echo "============================================================"
echo "        MOTOR TRIAGE DEMO - STARTING"
echo "============================================================"
echo ""

# ------------------------------------------------------------
# Function: check if a port is already being used
# ------------------------------------------------------------

check_port() {
    local PORT=$1

    if (echo > /dev/tcp/127.0.0.1/$PORT) >/dev/null 2>&1; then
        echo "[ERROR] Port $PORT is already in use."
        echo "        Please stop the existing application first."
        exit 1
    fi
}

# ------------------------------------------------------------
# Check required ports
# ------------------------------------------------------------

echo "[1/5] Checking ports..."

check_port 8500
check_port 8501
check_port 8502
check_port 5000

echo "      Ports are available."
echo ""

# ------------------------------------------------------------
# Function to start a process in its own process group
# ------------------------------------------------------------

start_process() {
    local NAME=$1
    local COMMAND=$2
    local LOG_FILE=$3

    echo "Starting $NAME..."

    setsid bash -c "$COMMAND" > "$LOG_FILE" 2>&1 &

    local PID=$!

    echo "$PID" > "$LOG_DIR/${NAME// /_}.pid"

    echo "      PID: $PID"
    echo "      Log: $LOG_FILE"

    sleep 2
}

# ------------------------------------------------------------
# Wait until a port becomes available
# ------------------------------------------------------------

wait_for_port() {
    local PORT=$1
    local NAME=$2

    echo "      Waiting for $NAME on port $PORT..."

    for i in {1..30}; do

        if (echo > /dev/tcp/127.0.0.1/$PORT) >/dev/null 2>&1; then
            echo "      $NAME is running."
            return 0
        fi

        sleep 1

    done

    echo ""
    echo "[ERROR] $NAME did not start successfully."
    echo ""
    echo "Check the log file:"
    echo "$LOG_DIR"
    exit 1
}

# ============================================================
# 1. MCP SERVER
# ============================================================

start_process \
    "MCP_Server" \
    "cd '$AGENTS_DIR' && '$VENV' MCP/main.py" \
    "$LOG_DIR/mcp.log"

wait_for_port 8500 "MCP Server"

echo ""

# ============================================================
# 2. INTAKE VALIDATION AGENT
# ============================================================

start_process \
    "Intake_Validation_Agent" \
    "cd '$AGENTS_DIR' && '$VENV' MotorIntakeValidationAgent/server.py" \
    "$LOG_DIR/intake_validation.log"

wait_for_port 8501 "Intake Validation Agent"

echo ""

# ============================================================
# 3. MOTOR TRIAGE AGENT
# ============================================================

start_process \
    "Motor_Triage_Agent" \
    "cd '$AGENTS_DIR' && '$VENV' MotorTriageAgent/server.py" \
    "$LOG_DIR/motor_triage.log"

wait_for_port 8502 "Motor Triage Agent"

echo ""

# ============================================================
# 4. MOTOR CLAIMS UI
# ============================================================

start_process \
    "Motor_Claims_UI" \
    "cd '$BASE_DIR/motor_claims' && npm run dev" \
    "$LOG_DIR/motor_claims_ui.log"

wait_for_port 5000 "Motor Claims UI"

echo ""
echo "============================================================"
echo "        MOTOR TRIAGE DEMO IS READY"
echo "============================================================"
echo ""
echo "MCP Server:             http://localhost:8500"
echo "Intake Validation:      http://localhost:8501"
echo "Motor Triage:           http://localhost:8502"
echo "Motor Claims UI:        http://localhost:5000"
echo ""
echo "Logs:"
echo "$LOG_DIR"
echo ""
echo "The SSH tunnel will remain active."
echo "Press Ctrl+C to stop the demo."
echo "============================================================"
echo ""

# ------------------------------------------------------------
# Keep SSH session alive.
# This is important because the Windows launcher uses
# SSH port forwarding through this connection.
# ------------------------------------------------------------

cleanup() {

    echo ""
    echo "Stopping Motor Triage Demo..."

    for PID_FILE in "$LOG_DIR"/*.pid; do

        if [ -f "$PID_FILE" ]; then

            PID=$(cat "$PID_FILE")

            if kill -0 "$PID" 2>/dev/null; then
                echo "Stopping PID $PID..."
                kill -- "-$PID" 2>/dev/null || kill "$PID" 2>/dev/null
            fi

            rm -f "$PID_FILE"

        fi

    done

    echo "Demo stopped."

}

trap cleanup EXIT INT TERM

while true; do
    sleep 60
done
