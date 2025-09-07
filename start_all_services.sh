#!/bin/bash

echo "Starting All Notification Services..."
echo

echo "[1/3] Starting WhatsApp API (Node.js) on port 5000..."
cd "$(dirname "$0")/Notification/NODEJS"
gnome-terminal --title="WhatsApp API" -- bash -c "node whatsapp.js; exec bash" 2>/dev/null || \
xterm -title "WhatsApp API" -e "node whatsapp.js; bash" 2>/dev/null || \
osascript -e 'tell app "Terminal" to do script "cd \"$(pwd)\" && node whatsapp.js"' 2>/dev/null || \
echo "Please start WhatsApp API manually: cd Notification/NODEJS && node whatsapp.js"

echo "[2/3] Starting Email API (FastAPI) on port 8000..."
cd "$(dirname "$0")/Notification/PYTHON"
gnome-terminal --title="Email API" -- bash -c "uvicorn send_email_api:app --reload --port 8000; exec bash" 2>/dev/null || \
xterm -title "Email API" -e "uvicorn send_email_api:app --reload --port 8000; bash" 2>/dev/null || \
osascript -e 'tell app "Terminal" to do script "cd \"$(pwd)\" && uvicorn send_email_api:app --reload --port 8000"' 2>/dev/null || \
echo "Please start Email API manually: cd Notification/PYTHON && uvicorn send_email_api:app --reload --port 8000"

echo "[3/3] Starting Notification Server (Python)..."
gnome-terminal --title="Notification Server" -- bash -c "python server.py; exec bash" 2>/dev/null || \
xterm -title "Notification Server" -e "python server.py; bash" 2>/dev/null || \
osascript -e 'tell app "Terminal" to do script "cd \"$(pwd)\" && python server.py"' 2>/dev/null || \
echo "Please start Notification Server manually: cd Notification/PYTHON && python server.py"

echo
echo "All services are starting..."
echo "- WhatsApp API: http://localhost:5000"
echo "- Email API: http://localhost:8000"
echo "- Notification Server: Running in background"
echo
echo "Press Enter to exit..."
read
