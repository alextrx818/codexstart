#!/bin/bash

# SSH Monitoring Start Script
# This script starts the project with SSH monitoring capabilities

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$SCRIPT_DIR/ssh_monitor.log"
PROJECT_LOG="$SCRIPT_DIR/start.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

print_error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

# Function to start SSH monitoring
start_ssh_monitoring() {
    print_status "Starting SSH connection monitoring..."
    
    # Monitor SSH connections and log them
    netstat -tn 2>/dev/null | grep ':22 ' | while read line; do
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] SSH Connection: $line" >> "$LOG_FILE"
    done
    
    # Monitor network traffic on SSH port
    if command -v ss >/dev/null 2>&1; then
        print_status "Monitoring SSH connections with ss command..."
        ss -tn state established '( dport = :22 or sport = :22 )' >> "$LOG_FILE" 2>&1
    fi
    
    # Log SSH authentication attempts
    if [ -f /var/log/auth.log ]; then
        print_status "Monitoring SSH authentication in auth.log..."
        tail -f /var/log/auth.log | grep -i ssh >> "$LOG_FILE" 2>&1 &
    elif [ -f /var/log/secure ]; then
        print_status "Monitoring SSH authentication in secure log..."
        tail -f /var/log/secure | grep -i ssh >> "$LOG_FILE" 2>&1 &
    fi
}

# Function to monitor project data flow
monitor_data_flow() {
    print_status "Starting data flow monitoring..."
    
    # Monitor file changes in real-time
    if command -v inotifywait >/dev/null 2>&1; then
        print_status "Using inotifywait for file monitoring..."
        inotifywait -m -r "$SCRIPT_DIR" -e modify,create,delete --format '%T %w%f %e' --timefmt '%Y-%m-%d %H:%M:%S' >> "$LOG_FILE" 2>&1 &
    else
        print_status "Installing inotify-tools for file monitoring..."
        apt-get update && apt-get install -y inotify-tools
        inotifywait -m -r "$SCRIPT_DIR" -e modify,create,delete --format '%T %w%f %e' --timefmt '%Y-%m-%d %H:%M:%S' >> "$LOG_FILE" 2>&1 &
    fi
    
    # Monitor network connections
    print_status "Starting network monitoring..."
    netstat -tuln | grep LISTEN >> "$LOG_FILE" 2>&1
    
    # Monitor process activity
    print_status "Starting process monitoring..."
    ps aux | grep -E "(python|step)" | grep -v grep >> "$LOG_FILE" 2>&1
}

# Stop any existing processes
print_status "Stopping any existing project processes..."
./start.sh stop 2>/dev/null || true
pkill -f "step.*py" 2>/dev/null || true

# Clean old logs
> "$LOG_FILE"
> "$PROJECT_LOG"

print_status "========================================="
print_status "Starting Project with SSH Monitoring"
print_status "========================================="

# Start SSH monitoring
start_ssh_monitoring

# Start data flow monitoring  
monitor_data_flow

# Start the main project
print_status "Starting main project..."
./start.sh start

# Check if project started successfully
sleep 3
if ./start.sh status | grep -q "RUNNING"; then
    print_success "✓ Project started successfully with monitoring"
    print_status "SSH Monitor Log: $LOG_FILE"
    print_status "Project Log: $PROJECT_LOG"
    print_status ""
    print_status "Monitoring active for:"
    print_status "  • SSH connections and authentication"
    print_status "  • File system changes"
    print_status "  • Network connections"
    print_status "  • Process activity"
    print_status ""
    print_status "Use 'tail -f $LOG_FILE' to view live monitoring"
    print_status "Use './start.sh logs' to view project logs"
else
    print_error "✗ Failed to start project"
    exit 1
fi
