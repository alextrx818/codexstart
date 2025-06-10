#!/bin/bash

# Configuration
PIPELINE_DIR="/root/6-4-2025"
LOG_FILE="pipeline_monitor.log"

# Start pipeline
cd $PIPELINE_DIR
./start.sh start &
PIPELINE_PID=$!

echo "Pipeline started with PID $PIPELINE_PID" | tee -a $LOG_FILE

# Monitor file access
inotifywait -m -r --format '%T %w%f %e' --timefmt '%F %T' \
    -e access,open,close_write \
    $PIPELINE_DIR \
| grep --line-buffered "step7" \
| tee -a $LOG_FILE &
MONITOR_PID=$!

echo "Monitoring started with PID $MONITOR_PID" | tee -a $LOG_FILE

# Cleanup function
cleanup() {
    kill $PIPELINE_PID $MONITOR_PID
    wait
    echo "Monitoring stopped" | tee -a $LOG_FILE
}

trap cleanup EXIT

# Keep script running
wait
