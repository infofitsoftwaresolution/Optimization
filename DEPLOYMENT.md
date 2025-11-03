# AWS EC2 Deployment Guide

## Prerequisites
- AWS EC2 instance running Ubuntu/Linux
- Python 3.8+ installed
- AWS credentials configured (via IAM role or AWS CLI)

## Deployment Steps

### 1. Transfer Files to EC2
```bash
# From your local machine
scp -r AICostOptimizer/ ubuntu@your-ec2-ip:~/
```

### 2. SSH into EC2
```bash
ssh ubuntu@your-ec2-ip
```

### 3. Install Dependencies
```bash
cd ~/AICostOptimizer
sudo apt-get update
sudo apt-get install -y python3-pip
pip3 install -r requirements.txt
```

### 4. Configure AWS Credentials
```bash
# Option 1: Use IAM Role (Recommended)
# Attach IAM role with Bedrock permissions to EC2 instance

# Option 2: Configure AWS CLI
aws configure
```

### 5. Configure Firewall (Security Group)
- Open port 8501 in EC2 Security Group
- Source: 0.0.0.0/0 (or your IP for security)

### 6. Start Dashboard
```bash
cd ~/AICostOptimizer
chmod +x start_dashboard.sh
./start_dashboard.sh
```

### 7. Run as Background Service (Optional)
```bash
# Using nohup
nohup ./start_dashboard.sh > dashboard.log 2>&1 &

# Or create systemd service
sudo nano /etc/systemd/system/aicostoptimizer.service
```

### Systemd Service Example
```ini
[Unit]
Description=AI Cost Optimizer Dashboard
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/AICostOptimizer
ExecStart=/usr/bin/python3 -m streamlit run src/dashboard.py --server.port 8501 --server.address 0.0.0.0
Restart=always

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl daemon-reload
sudo systemctl enable aicostoptimizer
sudo systemctl start aicostoptimizer
sudo systemctl status aicostoptimizer
```

### 8. Access Dashboard
Open browser: `http://your-ec2-ip:8501`

## Environment Variables (Optional)
Create `.env` file:
```bash
AWS_REGION=us-east-2
AWS_DEFAULT_REGION=us-east-2
```

## Monitoring
- View logs: `tail -f dashboard.log`
- Check process: `ps aux | grep streamlit`
- Check port: `netstat -tlnp | grep 8501`

## Security Recommendations
1. Use IAM roles instead of access keys
2. Restrict Security Group to your IP
3. Consider using HTTPS (nginx reverse proxy)
4. Keep packages updated: `pip3 install -r requirements.txt --upgrade`

