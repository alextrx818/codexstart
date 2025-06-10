#!/bin/bash

# Verbose pipeline starter
LOG_FILE="verbose_start.log"

echo "[$(date)] Starting pipeline in verbose mode" | tee $LOG_FILE

# Step 1: Stop existing
/root/6-4-2025/start.sh stop | tee -a $LOG_FILE

echo "[$(date)] Activating virtual environment" | tee -a $LOG_FILE
source /root/6-4-2025/venv/bin/activate

# Step 2: Install dependencies
pip install -r /root/6-4-2025/requirements.txt | tee -a $LOG_FILE

# Step 3: Run step1.py
echo "[$(date)] Starting step1.py" | tee -a $LOG_FILE
python /root/6-4-2025/step1.py 2>&1 | tee -a $LOG_FILE &

echo "[$(date)] Pipeline started in verbose mode" | tee -a $LOG_FILE
