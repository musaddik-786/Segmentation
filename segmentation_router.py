The processes are still crashing immediately. The logs will tell us exactly why. Since VS Code is already connected to the VM (I can see `SSH: 20.40.57.76` in the status bar), open a terminal in VS Code and run:

```bash
cat /tmp/motor_demo_logs/mcp.log
```

```bash
cat /tmp/motor_demo_logs/triage.log
```

```bash
cat /tmp/motor_demo_logs/intake.log
```

Also verify the Python path is correct on the VM:

```bash
ls /home/azureuser/Ramakrishna/claims-SLM-Finetune/slm-env/bin/python
```

And confirm the script was updated correctly:

```bash
head -5 /home/azureuser/Ramakrishna/claims-SLM-Finetune/start_services.sh
```

The output from those log files will show the exact crash reason — paste what you see and I'll fix it immediately. The most common causes at this stage are: a missing environment variable (like an API key), a Python import error, or a config file the agents need that isn't in the expected path.
