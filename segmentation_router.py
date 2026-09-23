so currently i am having a project on vs code under Ramakrishna repository it has a folder named claims-SLM-Finetune and under it i have to Run 4 terminals as given below and for the last terminal i have to forward the port 5000 


Run each in its own terminal. Order matters: MCP first, then agents, then app.
Terminal 1 — MCP server (port 8500):
bash
cd /home/azureuser/Ramakrishna/claims-SLM-Finetune/MotorTriageAgents
../slm-env/bin/python MCP/main.py
Terminal 2 — Intake Validation Agent (port 8501):
bash
cd /home/azureuser/Ramakrishna/claims-SLM-Finetune/MotorTriageAgents
../slm-env/bin/python MotorIntakeValidationAgent/server.py
Terminal 3 — Motor Triage Agent (port 8502):
bash
cd /home/azureuser/Ramakrishna/claims-SLM-Finetune/MotorTriageAgents
../slm-env/bin/python MotorTriageAgent/server.py
Terminal 4 — Replit App / UI (port 5000):
bash
cd /home/azureuser/Ramakrishna/claims-SLM-Finetune/motor_claims
npm run dev
Then open http://localhost:5000.





