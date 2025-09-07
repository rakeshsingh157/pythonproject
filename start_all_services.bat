@echo off
echo Starting All Notification Services...
echo.

echo [1/3] Starting WhatsApp API (Node.js) on port 5000...
start "WhatsApp API" cmd /k "cd /d "%~dp0Notification\NODEJS" && node whatsapp.js"

echo [2/3] Starting Email API (FastAPI) on port 8000...
start "Email API" cmd /k "cd /d "%~dp0Notification\PYTHON" && uvicorn send_email_api:app --reload --port 8000"

echo [3/3] Starting Notification Server (Python)...
start "Notification Server" cmd /k "cd /d "%~dp0Notification\PYTHON" && python server.py"

echo.
echo All services are starting...
echo - WhatsApp API: http://localhost:5000
echo - Email API: http://localhost:8000
echo - Notification Server: Running in background
echo.
echo Press any key to exit...
pause >nul
