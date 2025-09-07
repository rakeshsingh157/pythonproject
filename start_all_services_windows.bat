@echo off
setlocal enabledelayedexpansion

echo ==========================================
echo Starting All Notification Services - Windows
echo ==========================================
echo.

REM Colors (Windows 10+)
for /f %%a in ('echo prompt $E ^| cmd') do set "ESC=%%a"
set "GREEN=%ESC%[32m"
set "YELLOW=%ESC%[33m"
set "RED=%ESC%[31m"
set "BLUE=%ESC%[34m"
set "NC=%ESC%[0m"

REM Get script directory
set "SCRIPT_DIR=%~dp0"

REM Function to check if port is in use
:check_port
set "port=%1"
netstat -an | findstr ":%port% " >nul
if %errorlevel% equ 0 (
    echo %RED%Port %port% is already in use!%NC%
    exit /b 1
)
exit /b 0

REM Check port availability
echo Checking port availability...
call :check_port 5000
if %errorlevel% neq 0 exit /b 1
call :check_port 8000
if %errorlevel% neq 0 exit /b 1
echo %GREEN%All ports are available%NC%
echo.

REM Create logs directory
if not exist "logs" mkdir logs

REM Start WhatsApp API (Node.js)
echo %BLUE%[1/3] WhatsApp API (Port 5000)%NC%
echo %YELLOW%Starting WhatsApp API...%NC%
start "WhatsApp API" /min cmd /c "cd /d "%SCRIPT_DIR%Notification\NODEJS" && node whatsapp.js > "%SCRIPT_DIR%logs\whatsapp.log" 2>&1"
timeout /t 3 /nobreak >nul

REM Start Email API (FastAPI)
echo %BLUE%[2/3] Email API (Port 8000)%NC%
echo %YELLOW%Starting Email API...%NC%
start "Email API" /min cmd /c "cd /d "%SCRIPT_DIR%Notification\PYTHON" && uvicorn send_email_api:app --reload --port 8000 > "%SCRIPT_DIR%logs\email.log" 2>&1"
timeout /t 3 /nobreak >nul

REM Start Notification Server (Python)
echo %BLUE%[3/3] Notification Server%NC%
echo %YELLOW%Starting Notification Server...%NC%
start "Notification Server" /min cmd /c "cd /d "%SCRIPT_DIR%Notification\PYTHON" && python server.py > "%SCRIPT_DIR%logs\notification.log" 2>&1"
timeout /t 3 /nobreak >nul

echo.
echo ==========================================
echo %GREEN%All services started successfully!%NC%
echo ==========================================
echo.
echo %YELLOW%Service URLs:%NC%
echo   WhatsApp API: http://localhost:5000
echo   Email API: http://localhost:8000
echo   Notification Server: Running in background
echo.
echo %YELLOW%Log Files:%NC%
echo   WhatsApp: %SCRIPT_DIR%logs\whatsapp.log
echo   Email: %SCRIPT_DIR%logs\email.log
echo   Notification: %SCRIPT_DIR%logs\notification.log
echo.
echo %YELLOW%Process Management:%NC%
echo   To view running processes: tasklist ^| findstr /i "node python uvicorn"
echo   To stop all services: stop_all_services_windows.bat
echo   To view logs: type logs\*.log
echo.
echo %BLUE%Services are running in minimized windows.%NC%
echo %BLUE%Check the taskbar for service windows.%NC%
echo.
pause
