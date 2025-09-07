#!/bin/bash

# AWS Linux script to stop all notification services

echo "=========================================="
echo "Stopping All Notification Services"
echo "=========================================="
echo

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to stop service
stop_service() {
    local service_name=$1
    local pid_file="${service_name}.pid"
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if ps -p $pid > /dev/null 2>&1; then
            echo -e "${YELLOW}Stopping $service_name (PID: $pid)...${NC}"
            kill $pid
            sleep 2
            
            # Force kill if still running
            if ps -p $pid > /dev/null 2>&1; then
                echo -e "${RED}Force killing $service_name...${NC}"
                kill -9 $pid
            fi
            
            echo -e "${GREEN}$service_name stopped${NC}"
        else
            echo -e "${YELLOW}$service_name was not running${NC}"
        fi
        rm -f "$pid_file"
    else
        echo -e "${YELLOW}No PID file found for $service_name${NC}"
    fi
}

# Stop all services
stop_service "whatsapp-api"
stop_service "email-api"
stop_service "notification-server"

# Also kill any remaining processes by port
echo
echo "Checking for remaining processes..."

# Kill processes on port 5000 (WhatsApp API)
if netstat -tuln | grep -q ":5000 "; then
    echo -e "${YELLOW}Killing processes on port 5000...${NC}"
    fuser -k 5000/tcp 2>/dev/null || true
fi

# Kill processes on port 8000 (Email API)
if netstat -tuln | grep -q ":8000 "; then
    echo -e "${YELLOW}Killing processes on port 8000...${NC}"
    fuser -k 8000/tcp 2>/dev/null || true
fi

echo
echo "=========================================="
echo -e "${GREEN}All services stopped successfully!${NC}"
echo "=========================================="
