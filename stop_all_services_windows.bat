@echo off
setlocal enabledelayedexpansion

echo ==========================================
echo Stopping All Notification Services - Windows
echo ==========================================
echo.

REM Colors (Windows 10+)
for /f %%a in ('echo prompt $E ^| cmd') do set "ESC=%%a"
set "GREEN=%ESC%[32m"
set "YELLOW=%ESC%[33m"
set "RED=%ESC%[31m"
set "NC=%ESC%[0m"

REM Function to kill process by name
:kill_process
set "process_name=%1"
echo %YELLOW%Stopping %process_name%...%NC%

REM Kill by process name
taskkill /f /im "%process_name%" >nul 2>&1
if %errorlevel% equ 0 (
    echo %GREEN%%process_name% stopped%NC%
) else (
    echo %YELLOW%%process_name% was not running%NC%
)

REM Kill by window title
taskkill /f /fi "WINDOWTITLE eq %process_name%*" >nul 2>&1
exit /b 0

REM Stop all services
call :kill_process "node.exe"
call :kill_process "python.exe"
call :kill_process "uvicorn.exe"

REM Kill processes by window titles
echo %YELLOW%Stopping service windows...%NC%
taskkill /f /fi "WINDOWTITLE eq WhatsApp API*" >nul 2>&1
taskkill /f /fi "WINDOWTITLE eq Email API*" >nul 2>&1
taskkill /f /fi "WINDOWTITLE eq Notification Server*" >nul 2>&1

REM Kill processes on specific ports
echo %YELLOW%Checking for processes on ports 5000 and 8000...%NC%

REM Find and kill processes on port 5000
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5000 "') do (
    if not "%%a"=="0" (
        echo %YELLOW%Killing process on port 5000 (PID: %%a)...%NC%
        taskkill /f /pid %%a >nul 2>&1
    )
)

REM Find and kill processes on port 8000
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000 "') do (
    if not "%%a"=="0" (
        echo %YELLOW%Killing process on port 8000 (PID: %%a)...%NC%
        taskkill /f /pid %%a >nul 2>&1
    )
)

echo.
echo ==========================================
echo %GREEN%All services stopped successfully!%NC%
echo ==========================================
echo.
echo %YELLOW%Verification:%NC%
echo   Checking if ports are free...
timeout /t 2 /nobreak >nul

netstat -an | findstr ":5000 " >nul
if %errorlevel% equ 0 (
    echo %RED%Port 5000 is still in use%NC%
) else (
    echo %GREEN%Port 5000 is free%NC%
)

netstat -an | findstr ":8000 " >nul
if %errorlevel% equ 0 (
    echo %RED%Port 8000 is still in use%NC%
) else (
    echo %GREEN%Port 8000 is free%NC%
)

echo.
pause
