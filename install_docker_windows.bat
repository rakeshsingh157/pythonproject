@echo off
setlocal enabledelayedexpansion

echo ==========================================
echo Docker Installation for Windows
echo ==========================================
echo.

REM Colors (Windows 10+)
for /f %%a in ('echo prompt $E ^| cmd') do set "ESC=%%a"
set "GREEN=%ESC%[32m"
set "YELLOW=%ESC%[33m"
set "RED=%ESC%[31m"
set "BLUE=%ESC%[34m"
set "NC=%ESC%[0m"

REM Check if running as administrator
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo %RED%This script requires administrator privileges.%NC%
    echo %YELLOW%Please run as administrator and try again.%NC%
    pause
    exit /b 1
)

echo %BLUE%Checking Docker installation...%NC%

REM Check if Docker Desktop is installed
docker --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f %%i in ('docker --version') do set DOCKER_VERSION=%%i
    echo %GREEN%Docker already installed: %DOCKER_VERSION%%NC%
    
    REM Check if Docker is running
    docker info >nul 2>&1
    if %errorlevel% equ 0 (
        echo %GREEN%Docker is running%NC%
    ) else (
        echo %YELLOW%Docker is installed but not running%NC%
        echo %YELLOW%Please start Docker Desktop and try again%NC%
        pause
        exit /b 1
    )
) else (
    echo %YELLOW%Docker not found. Installing Docker Desktop...%NC%
    
    REM Download Docker Desktop installer
    echo %BLUE%Downloading Docker Desktop installer...%NC%
    powershell -Command "& {Invoke-WebRequest -Uri 'https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe' -OutFile 'DockerDesktopInstaller.exe'}"
    
    if exist "DockerDesktopInstaller.exe" (
        echo %BLUE%Installing Docker Desktop...%NC%
        echo %YELLOW%This may take several minutes...%NC%
        
        REM Install Docker Desktop silently
        DockerDesktopInstaller.exe install --quiet --accept-license
        
        echo %GREEN%Docker Desktop installed successfully%NC%
        echo %YELLOW%Please restart your computer and start Docker Desktop%NC%
        echo %YELLOW%Then run this script again to verify installation%NC%
        
        REM Clean up installer
        del DockerDesktopInstaller.exe
        
        pause
        exit /b 0
    ) else (
        echo %RED%Failed to download Docker Desktop installer%NC%
        echo %YELLOW%Please download manually from: https://www.docker.com/products/docker-desktop/%NC%
        pause
        exit /b 1
    )
)

REM Check Docker Compose
echo %BLUE%Checking Docker Compose...%NC%
docker-compose --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f %%i in ('docker-compose --version') do set COMPOSE_VERSION=%%i
    echo %GREEN%Docker Compose already installed: %COMPOSE_VERSION%%NC%
) else (
    echo %YELLOW%Docker Compose not found. Installing...%NC%
    
    REM Download Docker Compose
    powershell -Command "& {Invoke-WebRequest -Uri 'https://github.com/docker/compose/releases/latest/download/docker-compose-Windows-x86_64.exe' -OutFile 'docker-compose.exe'}"
    
    if exist "docker-compose.exe" (
        move docker-compose.exe "C:\Windows\System32\docker-compose.exe"
        echo %GREEN%Docker Compose installed successfully%NC%
    ) else (
        echo %RED%Failed to download Docker Compose%NC%
    )
)

REM Enable WSL 2 (required for Docker Desktop)
echo %BLUE%Checking WSL 2...%NC%
wsl --status >nul 2>&1
if %errorlevel% neq 0 (
    echo %YELLOW%WSL 2 not found. Installing WSL 2...%NC%
    
    REM Enable WSL feature
    dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
    dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
    
    echo %YELLOW%WSL 2 features enabled. Please restart your computer.%NC%
    echo %YELLOW%After restart, run: wsl --set-default-version 2%NC%
)

REM Test Docker installation
echo %BLUE%Testing Docker installation...%NC%
docker run hello-world >nul 2>&1
if %errorlevel% equ 0 (
    echo %GREEN%Docker test successful%NC%
) else (
    echo %YELLOW%Docker test failed. Please check Docker Desktop is running%NC%
)

echo.
echo ==========================================
echo %GREEN%Docker setup completed!%NC%
echo ==========================================
echo.
echo %YELLOW%Next steps:%NC%
echo 1. Ensure Docker Desktop is running
echo 2. Deploy services: docker-compose -f docker-compose-windows.yml up -d
echo 3. Check status: docker-compose -f docker-compose-windows.yml ps
echo.
echo %YELLOW%Useful commands:%NC%
echo   Start services: docker-compose -f docker-compose-windows.yml up -d
echo   Stop services: docker-compose -f docker-compose-windows.yml down
echo   View logs: docker-compose -f docker-compose-windows.yml logs -f
echo   Check status: docker-compose -f docker-compose-windows.yml ps
echo.
pause
