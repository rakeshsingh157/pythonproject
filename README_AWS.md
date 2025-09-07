# AWS Linux Deployment Guide

This guide helps you deploy the notification services on AWS Linux (Amazon Linux 2/2023).

## 🚀 Quick Start

### Option 1: Manual Setup
```bash
# 1. Make setup script executable
chmod +x aws_setup.sh

# 2. Run setup (installs all dependencies)
./aws_setup.sh

# 3. Update environment variables
nano .env

# 4. Start all services
./start_all_services_aws.sh
```

### Option 2: Docker Deployment
```bash
# 1. Install Docker
sudo yum install -y docker
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -a -G docker ec2-user

# 2. Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 3. Deploy with Docker Compose
docker-compose -f docker-compose-aws.yml up -d
```

### Option 3: CloudFormation Stack
```bash
# Deploy entire infrastructure
aws cloudformation create-stack \
  --stack-name notification-services \
  --template-body file://aws_cloudformation.yaml \
  --parameters ParameterKey=KeyPairName,ParameterValue=your-key-pair \
  --capabilities CAPABILITY_IAM
```

## 📋 Prerequisites

- Amazon Linux 2/2023 EC2 instance
- Security group with ports 22, 5000, 8000 open
- At least 2GB RAM and 10GB storage
- Internet access for package installation

## 🔧 Services

| Service | Port | Purpose | URL |
|---------|------|---------|-----|
| WhatsApp API | 5000 | Send WhatsApp messages | http://your-ip:5000 |
| Email API | 8000 | Send email notifications | http://your-ip:8000 |
| Notification Server | - | Monitor database & trigger notifications | Background process |

## 📁 File Structure

```
├── aws_setup.sh                 # Complete setup script
├── start_all_services_aws.sh    # Start all services
├── stop_all_services_aws.sh     # Stop all services
├── docker-compose-aws.yml       # Docker deployment
├── aws_cloudformation.yaml      # Infrastructure as Code
├── .env                         # Environment variables
└── logs/                        # Service logs
    ├── whatsapp.log
    ├── email.log
    └── notification.log
```

## 🔐 Environment Variables

Create `.env` file with your configuration:

```bash
# Database Configuration
DB_HOST=your-database-host
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

1. **Launch EC2 Instance**
   - Use Amazon Linux 2 AMI
   - t3.medium or larger
   - Security group with ports 22, 5000, 8000

2. **Connect and Setup**
   ```bash
   ssh -i your-key.pem ec2-user@your-ip
   git clone your-repo
   cd your-repo
   chmod +x aws_setup.sh
   ./aws_setup.sh
   ```

3. **Configure Environment**
   ```bash
   nano .env  # Update with your values
   ```

4. **Start Services**
   ```bash
   ./start_all_services_aws.sh
   ```

5. **Authenticate WhatsApp**
   - Check logs: `tail -f logs/whatsapp.log`
   - Scan QR code with WhatsApp mobile app

## 🛠️ Management Commands

### Start/Stop Services
```bash
# Start all services
./start_all_services_aws.sh

# Stop all services
./stop_all_services_aws.sh

# Check service status
ps aux | grep -E "(node|python|uvicorn)"
```

### View Logs
```bash
# All logs
tail -f logs/*.log

# Individual logs
tail -f logs/whatsapp.log
tail -f logs/email.log
tail -f logs/notification.log
```

### Systemd Services (Optional)
```bash
# Enable auto-start
sudo systemctl enable whatsapp-api email-api notification-server

# Start services
sudo systemctl start whatsapp-api email-api notification-server

# Check status
sudo systemctl status whatsapp-api email-api notification-server
```

## 🔍 Monitoring

### Health Checks
```bash
# WhatsApp API
curl http://localhost:5000/health

# Email API
curl http://localhost:8000/docs
```

### Resource Usage
```bash
# CPU and Memory
top
htop

# Disk usage
df -h

# Network connections
netstat -tuln
```

## 🚨 Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   sudo netstat -tuln | grep :5000
   sudo fuser -k 5000/tcp
   ```

2. **Permission Denied**
   ```bash
   chmod +x *.sh
   sudo chown -R ec2-user:ec2-user .
   ```

3. **Node.js Not Found**
   ```bash
   curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
   sudo yum install -y nodejs
   ```

4. **Python Dependencies**
   ```bash
   python3.11 -m pip install --upgrade pip
   python3.11 -m pip install -r requirements.txt
   ```

### Log Analysis
```bash
# Check for errors
grep -i error logs/*.log

# Monitor real-time
tail -f logs/*.log | grep -i error
```

## 🔒 Security

- Use IAM roles instead of access keys
- Enable VPC with private subnets
- Use Application Load Balancer with SSL
- Regular security updates: `sudo yum update -y`
- Monitor CloudTrail logs

## 📈 Scaling

### Horizontal Scaling
- Use Application Load Balancer
- Deploy multiple instances
- Use RDS for database
- Implement auto-scaling groups

### Vertical Scaling
- Increase instance size
- Add more memory/CPU
- Use EBS optimized instances

## 💰 Cost Optimization

- Use Spot instances for development
- Implement auto-scaling
- Use CloudWatch for monitoring
- Regular cleanup of unused resources

## 📞 Support

For issues:
1. Check logs: `tail -f logs/*.log`
2. Verify environment: `cat .env`
3. Test connectivity: `curl http://localhost:5000/health`
4. Check system resources: `top`, `df -h`
