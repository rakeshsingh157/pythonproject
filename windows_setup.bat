@echo off
setlocal enabledelayedexpansion

echo ==========================================
echo Windows Setup for Notification Services
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

echo %BLUE%Checking system requirements...%NC%

REM Check if running as administrator
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo %RED%This script requires administrator privileges.%NC%
    echo %YELLOW%Please run as administrator and try again.%NC%
    pause
    exit /b 1
)

REM Check Windows version
for /f "tokens=4-5 delims=. " %%i in ('ver') do set VERSION=%%i.%%j
echo %GREEN%Windows Version: %VERSION%%NC%

REM Check if Node.js is installed
echo %BLUE%Checking Node.js installation...%NC%
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo %YELLOW%Node.js not found. Installing Node.js 18...%NC%
    
    REM Download and install Node.js 18
    powershell -Command "& {Invoke-WebRequest -Uri 'https://nodejs.org/dist/v18.19.0/node-v18.19.0-x64.msi' -OutFile 'nodejs-installer.msi'}"
    if exist "nodejs-installer.msi" (
        msiexec /i nodejs-installer.msi /quiet /norestart
        timeout /t 10 /nobreak >nul
        del nodejs-installer.msi
        echo %GREEN%Node.js installed successfully%NC%
    ) else (
        echo %RED%Failed to download Node.js installer%NC%
        echo %YELLOW%Please install Node.js manually from https://nodejs.org/%NC%
    )
) else (
    for /f %%i in ('node --version') do set NODE_VERSION=%%i
    echo %GREEN%Node.js already installed: %NODE_VERSION%%NC%
)

REM Check if Python is installed
echo %BLUE%Checking Python installation...%NC%
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo %YELLOW%Python not found. Installing Python 3.11...%NC%
    
    REM Download and install Python 3.11
    powershell -Command "& {Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.7/python-3.11.7-amd64.exe' -OutFile 'python-installer.exe'}"
    if exist "python-installer.exe" (
        python-installer.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
        timeout /t 15 /nobreak >nul
        del python-installer.exe
        echo %GREEN%Python installed successfully%NC%
    ) else (
        echo %RED%Failed to download Python installer%NC%
        echo %YELLOW%Please install Python manually from https://python.org/%NC%
    )
) else (
    for /f %%i in ('python --version') do set PYTHON_VERSION=%%i
    echo %GREEN%Python already installed: %PYTHON_VERSION%%NC%
)

REM Install Git if not present
echo %BLUE%Checking Git installation...%NC%
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo %YELLOW%Git not found. Installing Git...%NC%
    powershell -Command "& {Invoke-WebRequest -Uri 'https://github.com/git-for-windows/git/releases/download/v2.43.0.windows.1/Git-2.43.0-64-bit.exe' -OutFile 'git-installer.exe'}"
    if exist "git-installer.exe" (
        git-installer.exe /SILENT
        timeout /t 10 /nobreak >nul
        del git-installer.exe
        echo %GREEN%Git installed successfully%NC%
    )
) else (
    for /f %%i in ('git --version') do set GIT_VERSION=%%i
    echo %GREEN%Git already installed: %GIT_VERSION%%NC%
)

REM Refresh PATH environment variable
echo %BLUE%Refreshing environment variables...%NC%
call refreshenv

REM Install Node.js dependencies
echo %BLUE%Installing Node.js dependencies...%NC%
cd /d "%SCRIPT_DIR%Notification\NODEJS"
if exist "package.json" (
    npm install
    if %errorlevel% equ 0 (
        echo %GREEN%Node.js dependencies installed successfully%NC%
    ) else (
        echo %RED%Failed to install Node.js dependencies%NC%
    )
) else (
    echo %YELLOW%package.json not found in Notification\NODEJS%NC%
)

REM Install Python dependencies
echo %BLUE%Installing Python dependencies...%NC%
cd /d "%SCRIPT_DIR%Notification\PYTHON"
if exist "requirements.txt" (
    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt
    if %errorlevel% equ 0 (
        echo %GREEN%Python dependencies installed successfully%NC%
    ) else (
        echo %RED%Failed to install Python dependencies%NC%
    )
) else (
    echo %YELLOW%requirements.txt not found in Notification\PYTHON%NC%
)

REM Create necessary directories
echo %BLUE%Creating directories...%NC%
cd /d "%SCRIPT_DIR%"
if not exist "logs" mkdir logs
if not exist "Notification\NODEJS\session" mkdir "Notification\NODEJS\session"
echo %GREEN%Directories created successfully%NC%

REM Create environment file
echo %BLUE%Creating environment configuration...%NC%
if not exist ".env" (
    (
        echo # Database Configuration
        echo DB_HOST=localhost
        echo DB_USER=your_db_user
        echo DB_PASSWORD=your_db_password
        echo DB_NAME=your_db_name
        echo.
        echo # Google Gemini API
        echo GOOGLE_GEMINI_API_KEY=your_gemini_api_key
        echo.
        echo # Email Configuration
        echo EMAIL_SENDER=your_email@gmail.com
        echo EMAIL_PASSWORD=your_app_password
    ) > .env
    echo %GREEN%Environment file created: .env%NC%
    echo %YELLOW%Please update .env with your actual values%NC%
) else (
    echo %GREEN%Environment file already exists%NC%
)

REM Create Windows Service scripts
echo %BLUE%Creating Windows Service scripts...%NC%

REM WhatsApp API Service
(
    echo @echo off
    echo cd /d "%SCRIPT_DIR%Notification\NODEJS"
    echo node whatsapp.js
) > "whatsapp-service.bat"

REM Email API Service
(
    echo @echo off
    echo cd /d "%SCRIPT_DIR%Notification\PYTHON"
    echo uvicorn send_email_api:app --reload --port 8000
) > "email-service.bat"

REM Notification Server Service
(
    echo @echo off
    echo cd /d "%SCRIPT_DIR%Notification\PYTHON"
    echo python server.py
) > "notification-service.bat"

echo %GREEN%Service scripts created successfully%NC%

REM Create Windows Task Scheduler entries (optional)
echo %BLUE%Creating Windows Task Scheduler entries...%NC%
schtasks /create /tn "WhatsApp API" /tr "%SCRIPT_DIR%whatsapp-service.bat" /sc onstart /ru "SYSTEM" /f >nul 2>&1
schtasks /create /tn "Email API" /tr "%SCRIPT_DIR%email-service.bat" /sc onstart /ru "SYSTEM" /f >nul 2>&1
schtasks /create /tn "Notification Server" /tr "%SCRIPT_DIR%notification-service.bat" /sc onstart /ru "SYSTEM" /f >nul 2>&1
echo %GREEN%Task Scheduler entries created%NC%

echo.
echo ==========================================
echo %GREEN%Windows setup completed successfully!%NC%
echo ==========================================
echo.
echo %YELLOW%Next steps:%NC%
echo 1. Update .env file with your actual configuration
echo 2. Start services: start_all_services_windows.bat
echo 3. Or use individual service scripts
echo.
echo %YELLOW%Useful commands:%NC%
echo   Start all services: start_all_services_windows.bat
echo   Stop all services: stop_all_services_windows.bat
echo   View logs: type logs\*.log
echo   Check services: tasklist ^| findstr /i "node python uvicorn"
echo.
echo %YELLOW%Windows Services:%NC%
echo   Services are configured to start automatically
echo   Manage via Task Scheduler or service scripts
echo.
pause
