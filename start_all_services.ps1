Write-Host "Starting All Notification Services..." -ForegroundColor Green
Write-Host ""

# Function to start service in new window
function Start-ServiceWindow {
    param(
        [string]$Title,
        [string]$Command,
        [string]$WorkingDirectory
    )
    
    Write-Host "[$Title] Starting..." -ForegroundColor Yellow
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$WorkingDirectory'; $Command" -WindowStyle Normal
    Start-Sleep 2
}

# Start WhatsApp API
Start-ServiceWindow -Title "1/3 WhatsApp API" -Command "node whatsapp.js" -WorkingDirectory "$PSScriptRoot\Notification\NODEJS"

# Start Email API  
Start-ServiceWindow -Title "2/3 Email API" -Command "uvicorn send_email_api:app --reload --port 8000" -WorkingDirectory "$PSScriptRoot\Notification\PYTHON"

# Start Notification Server
Start-ServiceWindow -Title "3/3 Notification Server" -Command "python server.py" -WorkingDirectory "$PSScriptRoot\Notification\PYTHON"

Write-Host ""
Write-Host "All services are starting..." -ForegroundColor Green
Write-Host "- WhatsApp API: http://localhost:5000" -ForegroundColor Cyan
Write-Host "- Email API: http://localhost:8000" -ForegroundColor Cyan  
Write-Host "- Notification Server: Running in background" -ForegroundColor Cyan
Write-Host ""
Write-Host "Services will open in separate windows." -ForegroundColor Yellow
Write-Host "Press any key to exit this launcher..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
