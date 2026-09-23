so currently i am having a project on vs code under Ramakrishna repository it has a folder named claims-SLM-Finetune and 
under it i have to Run 4 terminals as given below and for the last terminal i have to forward the port to 5000 
so this is how i am running the application right now 


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


so vm is on ssh azureuser@20.40.57.76
and it has a password to connect

but now i have been told that there is a demo that my manager has to give and he told me that create a seperate file any file eg .sh file or whatever
and that file should be executed in windows terminal or bash or whatever so basically manager is not supposed to open the vs code nor he is supposed 
to open vs code terminal nor he is supposed to run those 4 terminals so, that is without opening anyofthis just by running that 1 file he should be able to run this project 


