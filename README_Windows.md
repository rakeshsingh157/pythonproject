# Windows Deployment Guide

This guide helps you deploy the notification services on Windows (Windows 10/11, Windows Server).

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)
```cmd
REM Run as Administrator
windows_setup.bat
start_all_services_windows.bat
```

### Option 2: Docker Deployment
```cmd
REM Install Docker first
install_docker_windows.bat

REM Deploy with Docker Compose
docker-compose -f docker-compose-windows.yml up -d
```

### Option 3: Manual Setup
```cmd
REM Install dependencies manually
REM Node.js: https://nodejs.org/
REM Python: https://python.org/
REM Git: https://git-scm.com/

REM Install packages
cd Notification\NODEJS
npm install

cd ..\PYTHON
pip install -r requirements.txt

REM Start services
start_all_services_windows.bat
```

## 📋 Prerequisites

- Windows 10/11 or Windows Server 2019+
- Administrator privileges
- Internet connection for package installation
- At least 4GB RAM and 10GB free disk space

## 🔧 Services

| Service | Port | Purpose | URL |
|---------|------|---------|-----|
| WhatsApp API | 5000 | Send WhatsApp messages | http://localhost:5000 |
| Email API | 8000 | Send email notifications | http://localhost:8000 |
| Notification Server | - | Monitor database & trigger notifications | Background process |

## 📁 File Structure

```
├── windows_setup.bat              # Complete setup script
├── start_all_services_windows.bat # Start all services
├── stop_all_services_windows.bat  # Stop all services
├── install_docker_windows.bat     # Docker installation
├── docker-compose-windows.yml     # Docker deployment
├── .env                           # Environment variables
├── logs/                          # Service logs
│   ├── whatsapp.log
│   ├── email.log
│   └── notification.log
└── service scripts/
    ├── whatsapp-service.bat
    ├── email-service.bat
    └── notification-service.bat
```

## 🔐 Environment Variables

Create `.env` file with your configuration:

```bash
# Database Configuration
DB_HOST=localhost
DB_USER=your-db-user
DB_PASSWORD=your-db-password
DB_NAME=your-db-name

# Google Gemini API
GOOGLE_GEMINI_API_KEY=your-gemini-api-key

# Email Configuration
EMAIL_SENDER=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
```

## 🎯 First Time Setup

1. **Download/Clone Project**
   ```cmd
   git clone your-repo
   cd your-repo
   ```

2. **Run Setup (As Administrator)**
   ```cmd
   windows_setup.bat
   ```

3. **Configure Environment**
   ```cmd
   notepad .env  # Update with your values
   ```

4. **Start Services**
   ```cmd
   start_all_services_windows.bat
   ```

5. **Authenticate WhatsApp**
   - Check logs: `type logs\whatsapp.log`
   - Scan QR code with WhatsApp mobile app

## 🛠️ Management Commands

### Start/Stop Services
```cmd
REM Start all services
start_all_services_windows.bat

REM Stop all services
stop_all_services_windows.bat

REM Check running processes
tasklist | findstr /i "node python uvicorn"
```

### View Logs
```cmd
REM All logs
type logs\*.log

REM Individual logs
type logs\whatsapp.log
type logs\email.log
type logs\notification.log

REM Real-time monitoring
powershell Get-Content logs\whatsapp.log -Wait
```

### Windows Services (Optional)
```cmd
REM Services are configured to start automatically
REM Manage via Task Scheduler or service scripts

REM Start individual services
whatsapp-service.bat
email-service.bat
notification-service.bat
```

## 🔍 Monitoring

### Health Checks
```cmd
REM WhatsApp API
curl http://localhost:5000/health

REM Email API
curl http://localhost:8000/docs
```

### Resource Usage
```cmd
REM Task Manager
taskmgr

REM Process Monitor
tasklist /svc

REM Network connections
netstat -an | findstr ":5000"
netstat -an | findstr ":8000"
```

## 🚨 Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```cmd
   netstat -an | findstr ":5000"
   taskkill /f /im node.exe
   ```

2. **Permission Denied**
   ```cmd
   REM Run as Administrator
   ```

3. **Node.js Not Found**
   ```cmd
   REM Reinstall Node.js from https://nodejs.org/
   REM Or run: windows_setup.bat
   ```

4. **Python Dependencies**
   ```cmd
   cd Notification\PYTHON
   python -m pip install --upgrade pip
   python -m pip install -r requirements.txt
   ```

5. **Docker Issues**
   ```cmd
   REM Ensure Docker Desktop is running
   REM Check WSL 2 is enabled
   ```

### Log Analysis
```cmd
REM Check for errors
findstr /i "error" logs\*.log

REM Monitor real-time
powershell Get-Content logs\*.log -Wait | findstr /i "error"
```

## 🔒 Security

- Run as Administrator only when necessary
- Use Windows Defender or antivirus
- Keep Windows updated
- Use strong passwords in .env
- Enable Windows Firewall
- Regular security updates

## 📈 Performance Optimization

### Windows Settings
- Disable unnecessary startup programs
- Increase virtual memory
- Use SSD storage
- Close unused applications

### Service Optimization
- Monitor memory usage
- Adjust service priorities
- Use Windows Performance Toolkit

## 🐳 Docker Deployment

### Prerequisites
```cmd
REM Install Docker Desktop
install_docker_windows.bat
```

### Deploy
```cmd
REM Start all services
docker-compose -f docker-compose-windows.yml up -d

REM Check status
docker-compose -f docker-compose-windows.yml ps

REM View logs
docker-compose -f docker-compose-windows.yml logs -f
```

### Management
```cmd
REM Stop services
docker-compose -f docker-compose-windows.yml down

REM Restart services
docker-compose -f docker-compose-windows.yml restart

REM Update services
docker-compose -f docker-compose-windows.yml up -d --build
```

## 🔄 Auto-Start Configuration

### Task Scheduler
Services are automatically configured to start on Windows boot via Task Scheduler.

### Manual Configuration
```cmd
REM Create scheduled tasks
schtasks /create /tn "WhatsApp API" /tr "C:\path\to\whatsapp-service.bat" /sc onstart
schtasks /create /tn "Email API" /tr "C:\path\to\email-service.bat" /sc onstart
schtasks /create /tn "Notification Server" /tr "C:\path\to\notification-service.bat" /sc onstart
```

## 📞 Support

For issues:
1. Check logs: `type logs\*.log`
2. Verify environment: `type .env`
3. Test connectivity: `curl http://localhost:5000/health`
4. Check system resources: Task Manager
5. Verify Windows services: Services.msc

## 🎯 Best Practices

- Always run setup as Administrator
- Keep dependencies updated
- Monitor system resources
- Regular backup of configuration
- Use Windows Event Viewer for system logs
- Enable Windows Update
- Use Windows Defender
