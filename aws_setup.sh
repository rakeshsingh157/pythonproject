#!/bin/bash

# AWS Linux setup script for notification services
# Installs all required dependencies and prepares the environment

echo "=========================================="
echo "AWS Linux Setup for Notification Services"
echo "=========================================="
echo

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Update system packages
echo -e "${BLUE}Updating system packages...${NC}"
sudo yum update -y

# Install Node.js 18
echo -e "${BLUE}Installing Node.js 18...${NC}"
if ! command_exists node; then
    curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
    sudo yum install -y nodejs
    echo -e "${GREEN}Node.js installed: $(node --version)${NC}"
else
    echo -e "${YELLOW}Node.js already installed: $(node --version)${NC}"
fi

# Install Python 3.11
echo -e "${BLUE}Installing Python 3.11...${NC}"
if ! command_exists python3.11; then
    sudo yum install -y python3.11 python3.11-pip python3.11-devel
    echo -e "${GREEN}Python 3.11 installed: $(python3.11 --version)${NC}"
else
    echo -e "${YELLOW}Python 3.11 already installed: $(python3.11 --version)${NC}"
fi

# Install system dependencies
echo -e "${BLUE}Installing system dependencies...${NC}"
sudo yum install -y \
    git \
    curl \
    wget \
    net-tools \
    chromium \
    gcc \
    gcc-c++ \
    make \
    openssl-devel \
    libffi-devel \
    zlib-devel \
    bzip2-devel \
    readline-devel \
    sqlite-devel \
    xz-devel \
    tk-devel

# Install Node.js dependencies
echo -e "${BLUE}Installing Node.js dependencies...${NC}"
cd Notification/NODEJS
npm install
cd ../..

# Install Python dependencies
echo -e "${BLUE}Installing Python dependencies...${NC}"
cd Notification/PYTHON
python3.11 -m pip install --upgrade pip
python3.11 -m pip install -r requirements.txt
cd ../..

# Create necessary directories
echo -e "${BLUE}Creating directories...${NC}"
mkdir -p logs
mkdir -p Notification/NODEJS/session
chmod 755 logs
chmod 755 Notification/NODEJS/session

# Set up environment variables
echo -e "${BLUE}Setting up environment...${NC}"
if [ ! -f .env ]; then
    cat > .env << EOF
# Database Configuration
DB_HOST=localhost
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_NAME=your_db_name

# Google Gemini API
GOOGLE_GEMINI_API_KEY=your_gemini_api_key

# Email Configuration
EMAIL_SENDER=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
EOF
    echo -e "${YELLOW}Created .env file. Please update with your actual values.${NC}"
fi

# Make scripts executable
echo -e "${BLUE}Making scripts executable...${NC}"
chmod +x start_all_services_aws.sh
chmod +x stop_all_services_aws.sh
chmod +x aws_setup.sh

# Create systemd service files (optional)
echo -e "${BLUE}Creating systemd service files...${NC}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# WhatsApp API service
sudo tee /etc/systemd/system/whatsapp-api.service > /dev/null << EOF
[Unit]
Description=WhatsApp API Service
After=network.target

[Service]
Type=simple
User=ec2-user
WorkingDirectory=$SCRIPT_DIR/Notification/NODEJS
ExecStart=/usr/bin/node whatsapp.js
Restart=always
RestartSec=10
Environment=NODE_ENV=production

[Install]
WantedBy=multi-user.target
EOF

# Email API service
sudo tee /etc/systemd/system/email-api.service > /dev/null << EOF
[Unit]
Description=Email API Service
After=network.target

[Service]
Type=simple
User=ec2-user
WorkingDirectory=$SCRIPT_DIR/Notification/PYTHON
ExecStart=/usr/bin/python3.11 -m uvicorn send_email_api:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10
Environment=PYTHONPATH=$SCRIPT_DIR/Notification/PYTHON

[Install]
WantedBy=multi-user.target
EOF

# Notification Server service
sudo tee /etc/systemd/system/notification-server.service > /dev/null << EOF
[Unit]
Description=Notification Server
After=network.target whatsapp-api.service email-api.service

[Service]
Type=simple
User=ec2-user
WorkingDirectory=$SCRIPT_DIR/Notification/PYTHON
ExecStart=/usr/bin/python3.11 server.py
Restart=always
RestartSec=10
Environment=PYTHONPATH=$SCRIPT_DIR/Notification/PYTHON

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd
sudo systemctl daemon-reload

echo
echo "=========================================="
echo -e "${GREEN}Setup completed successfully!${NC}"
echo "=========================================="
echo
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Update .env file with your actual configuration"
echo "2. Start services: ./start_all_services_aws.sh"
echo "3. Or use systemd: sudo systemctl start whatsapp-api email-api notification-server"
echo
echo -e "${YELLOW}Useful commands:${NC}"
echo "  Start all services: ./start_all_services_aws.sh"
echo "  Stop all services: ./stop_all_services_aws.sh"
echo "  View logs: tail -f logs/*.log"
echo "  Check status: sudo systemctl status whatsapp-api email-api notification-server"
echo
