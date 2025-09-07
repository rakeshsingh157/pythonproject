#!/bin/bash

# AWS Linux startup script for all notification services
# Compatible with Amazon Linux 2/2023, CentOS, RHEL

echo "=========================================="
echo "Starting All Notification Services on AWS"
echo "=========================================="
echo

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to check if port is in use
check_port() {
    local port=$1
    if netstat -tuln | grep -q ":$port "; then
        echo -e "${RED}Port $port is already in use!${NC}"
        return 1
    fi
    return 0
}

# Function to start service in background
start_service() {
    local service_name=$1
    local command=$2
    local working_dir=$3
    local log_file=$4
    
    echo -e "${YELLOW}[$service_name] Starting...${NC}"
    
    if [ -d "$working_dir" ]; then
        cd "$working_dir"
        nohup $command > "$log_file" 2>&1 &
        local pid=$!
        echo -e "${GREEN}[$service_name] Started with PID: $pid${NC}"
        echo $pid > "${service_name}.pid"
        sleep 2
    else
        echo -e "${RED}[$service_name] Directory not found: $working_dir${NC}"
        return 1
    fi
}

# Check if required ports are available
echo "Checking port availability..."
check_port 5000 || exit 1
check_port 8000 || exit 1
echo -e "${GREEN}All ports are available${NC}"
echo

# Create logs directory
mkdir -p logs

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Start WhatsApp API (Node.js)
echo -e "${BLUE}[1/3] WhatsApp API (Port 5000)${NC}"
start_service "whatsapp-api" "node whatsapp.js" "$SCRIPT_DIR/Notification/NODEJS" "$SCRIPT_DIR/logs/whatsapp.log"

# Start Email API (FastAPI)
echo -e "${BLUE}[2/3] Email API (Port 8000)${NC}"
start_service "email-api" "uvicorn send_email_api:app --host 0.0.0.0 --port 8000" "$SCRIPT_DIR/Notification/PYTHON" "$SCRIPT_DIR/logs/email.log"

# Start Notification Server (Python)
echo -e "${BLUE}[3/3] Notification Server${NC}"
start_service "notification-server" "python server.py" "$SCRIPT_DIR/Notification/PYTHON" "$SCRIPT_DIR/logs/notification.log"

echo
echo "=========================================="
echo -e "${GREEN}All services started successfully!${NC}"
echo "=========================================="
echo
echo -e "${YELLOW}Service URLs:${NC}"
echo -e "  WhatsApp API: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo 'localhost'):5000"
echo -e "  Email API: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo 'localhost'):8000"
echo -e "  Notification Server: Running in background"
echo
echo -e "${YELLOW}Log Files:${NC}"
echo -e "  WhatsApp: $SCRIPT_DIR/logs/whatsapp.log"
echo -e "  Email: $SCRIPT_DIR/logs/email.log"
echo -e "  Notification: $SCRIPT_DIR/logs/notification.log"
echo
echo -e "${YELLOW}Process IDs:${NC}"
echo -e "  WhatsApp API: $(cat whatsapp-api.pid 2>/dev/null || echo 'Not found')"
echo -e "  Email API: $(cat email-api.pid 2>/dev/null || echo 'Not found')"
echo -e "  Notification Server: $(cat notification-server.pid 2>/dev/null || echo 'Not found')"
echo
echo -e "${BLUE}To stop all services, run: ./stop_all_services_aws.sh${NC}"
echo -e "${BLUE}To view logs, run: tail -f logs/*.log${NC}"
