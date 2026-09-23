azureuser@slm-ft-t4:~/Ramakrishna/claims-SLM-Finetune$ sed -i 's|PYTHON=$BASE/../slm-env/bin/python|PYTHON=$BASE/slm-env/bin/python|' /home/azureuser/Ramakrishna/claims-SLM-Finetune/start_services.sh
azureuser@slm-ft-t4:~/Ramakrishna/claims-SLM-Finetune$ grep PYTHON /home/azureuser/Ramakrishna/claims-SLM-Finetune/start_services.sh
PYTHON=$BASE/slm-env/bin/python
nohup $PYTHON MCP/main.py > "$LOG_DIR/mcp.log" 2>&1 &
nohup $PYTHON MotorIntakeValidationAgent/server.py > "$LOG_DIR/intake.log" 2>&1 &
nohup $PYTHON MotorTriageAgent/server.py > "$LOG_DIR/triage.log" 2>&1 &
azureuser@slm-ft-t4:~/Ramakrishna/claims-SLM-Finetune$ bash /home/azureuser/Ramakrishna/claims-SLM-Finetune/start_services.sh
=== Motor Claims Demo — Service Startup ===
Base: /home/azureuser/Ramakrishna/claims-SLM-Finetune

[cleanup] Stopped existing process on port 5000 (PID 5112)
[1/4] MCP server started (PID 5270, port 8500) — waiting 10s...
[2/4] Intake Validation Agent started (PID 5304, port 8501) — waiting 10s...
[3/4] Motor Triage Agent started (PID 5339, port 8502) — waiting 20s for model load...
[4/4] Frontend app started (PID 5391, port 5000) — waiting 8s...

=== Port check ===
  [OK]  Port 8500 is listening
  [OK]  Port 8501 is listening
  [OK]  Port 8502 is listening
  [OK]  Port 5000 is listening

Logs: /tmp/motor_demo_logs/
Done. Port forwarding will connect now.
azureuser@slm-ft-t4:~/Ramakrishna/claims-SLM-Finetune$ 
