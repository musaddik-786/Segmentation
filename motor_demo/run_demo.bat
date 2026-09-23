@echo off
:: ============================================================
:: run_demo.bat — Motor Claims Demo Launcher
::
:: Double-click this file to:
::   1. Start all 4 services on the Azure VM
::   2. Forward port 5000 to your local machine
::   3. Open http://localhost:5000 in your browser
::
:: Prerequisites: run 1_setup_once.bat once before using this.
:: ============================================================

setlocal
set VM_USER=azureuser
set VM_HOST=20.40.57.76
set APP_PORT=5000
set KEY_FILE=%USERPROFILE%\.ssh\motor_demo_key
set REMOTE_SCRIPT=/home/azureuser/Ramakrishna/claims-SLM-Finetune/start_services.sh

title Motor Claims Demo

echo ============================================================
echo  Motor Claims Demo
echo  VM: %VM_USER%@%VM_HOST%
echo ============================================================
echo.

:: ── Check SSH is available ────────────────────────────────────────────────────
where ssh >nul 2>&1
if errorlevel 1 (
    echo [ERROR] SSH not found.
    echo         Install OpenSSH: Settings ^> Apps ^> Optional Features ^> OpenSSH Client
    pause
    exit /b 1
)

:: ── Check key exists (remind user to run setup if not) ───────────────────────
if not exist "%KEY_FILE%" (
    echo [ERROR] SSH key not found: %KEY_FILE%
    echo         Please run  1_setup_once.bat  first.
    pause
    exit /b 1
)

:: ── Step 1: Start all services on the VM ─────────────────────────────────────
echo [1/3] Starting services on VM...
echo       (This takes about 15 seconds for all 4 processes to come up)
echo.
ssh -i "%KEY_FILE%" -o StrictHostKeyChecking=accept-new -o BatchMode=yes %VM_USER%@%VM_HOST% "bash %REMOTE_SCRIPT%"
if errorlevel 1 (
    echo.
    echo [ERROR] Could not connect to VM or services failed to start.
    echo         Check that the VM is running at %VM_HOST%.
    pause
    exit /b 1
)

:: ── Step 2: Open browser ─────────────────────────────────────────────────────
echo.
echo [2/3] Opening browser at http://localhost:%APP_PORT%...
timeout /t 2 /nobreak >nul
start "" "http://localhost:%APP_PORT%"

:: ── Step 3: Port forward (keeps this window open — close to stop demo) ───────
echo.
echo [3/3] Port forwarding: localhost:%APP_PORT%  ──^>  VM:%APP_PORT%
echo.
echo ============================================================
echo  Demo is LIVE at http://localhost:%APP_PORT%
echo.
echo  Keep this window open while the demo runs.
echo  Close this window (or press Ctrl+C) to stop the tunnel.
echo ============================================================
echo.

ssh -i "%KEY_FILE%" -N -L %APP_PORT%:localhost:%APP_PORT% %VM_USER%@%VM_HOST%

:: ── Tunnel closed ─────────────────────────────────────────────────────────────
echo.
echo Demo tunnel closed. Services are still running on the VM.
echo (Re-run this file to reconnect.)
echo.
pause
