sed -i 's|PYTHON=$BASE/../slm-env/bin/python|PYTHON=$BASE/slm-env/bin/python|' /home/azureuser/Ramakrishna/claims-SLM-Finetune/start_services.sh

grep PYTHON /home/azureuser/Ramakrishna/claims-SLM-Finetune/start_services.sh

bash /home/azureuser/Ramakrishna/claims-SLM-Finetune/start_services.sh
