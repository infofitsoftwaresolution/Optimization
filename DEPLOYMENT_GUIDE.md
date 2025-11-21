# EC2 Deployment Guide

Complete guide to deploy the BellaTrix application to EC2 at `http://43.204.142.218/`

## 📋 Prerequisites

- EC2 instance running (Amazon Linux 2 or Ubuntu)
- SSH access to the EC2 instance
- GitHub repository with secrets configured
- Domain/IP: `43.204.142.218`

---

## 🚀 Step-by-Step Deployment

### Step 1: SSH into EC2 Instance

```bash
ssh -i your-key.pem ec2-user@43.204.142.218
```

**Note:** Replace `your-key.pem` with your actual SSH key file.

---

### Step 2: Install Required Software

#### Update System
```bash
# Amazon Linux 2
sudo yum update -y

# Ubuntu
sudo apt update && sudo apt upgrade -y
```

#### Install Python 3.10+
```bash
# Amazon Linux 2
sudo yum install -y python3.10 python3.10-pip python3.10-venv git

# Ubuntu
sudo apt install -y python3.10 python3.10-venv python3-pip git
```

#### Install Nginx
```bash
# Amazon Linux 2
sudo yum install -y nginx

# Ubuntu
sudo apt install -y nginx
```

#### Install GitHub CLI (for secrets)
```bash
# Amazon Linux 2
sudo yum install -y gh

# Ubuntu
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update
sudo apt install gh
```

---

### Step 3: Clone Repository

```bash
cd /home/ec2-user
git clone https://github.com/infofitsoftwaresolution/Optimization.git
cd Optimization
```

---

### Step 4: Set Up Environment from GitHub Secrets

```bash
# Make script executable
chmod +x scripts/setup-from-github-secrets.sh

# Run setup script
./scripts/setup-from-github-secrets.sh
```

This will:
- Install GitHub CLI if needed
- Authenticate with GitHub
- Download all secrets
- Create `.env` file automatically
- Set up the project

**If GitHub CLI authentication fails**, you can manually create `.env`:

```bash
# Create .env file manually
cat > .env << EOF
AWS_ACCESS_KEY_ID=your_key_here
AWS_SECRET_ACCESS_KEY=your_secret_here
AWS_REGION=us-east-2
DB_HOST=your_db_host
DB_PORT=5432
DB_NAME=bellatrix_db
DB_USER=postgres
DB_PASSWORD=your_password
OPENAI_API_KEY=your_openai_key
STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
EOF
```

---

### Step 5: Install Python Dependencies

```bash
# Create virtual environment
python3.10 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

---

### Step 6: Configure Nginx

```bash
# Copy nginx configuration
sudo cp nginx-optimization-app.conf /etc/nginx/conf.d/optimization-app.conf

# Test nginx configuration
sudo nginx -t

# Start and enable nginx
sudo systemctl start nginx
sudo systemctl enable nginx
```

**Important:** Make sure your EC2 Security Group allows:
- **Inbound Port 80** (HTTP) from `0.0.0.0/0`
- **Inbound Port 443** (HTTPS) if using SSL (optional)

---

### Step 7: Set Up Systemd Service

```bash
# Copy systemd service file
sudo cp streamlit-optimization.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable streamlit-optimization.service

# Start the service
sudo systemctl start streamlit-optimization.service

# Check status
sudo systemctl status streamlit-optimization.service
```

---

### Step 8: Verify Deployment

```bash
# Check Streamlit service
sudo systemctl status streamlit-optimization.service

# Check Nginx service
sudo systemctl status nginx

# Test local connection
curl http://localhost:8501

# Check logs if needed
sudo journalctl -u streamlit-optimization.service -f
```

---

### Step 9: Access Your Application

Open your browser and go to:
```
http://43.204.142.218/
```

You should see the landing page with sign up/sign in options.

---

## 🔄 Updating/Deploying New Changes

### Quick Update (Recommended)

```bash
cd /home/ec2-user/Optimization
chmod +x scripts/quick-deploy.sh
./scripts/quick-deploy.sh
```

### Full Deployment

```bash
cd /home/ec2-user/Optimization
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

### Manual Update

```bash
cd /home/ec2-user/Optimization

# Pull latest code
git pull origin main

# Update dependencies
source .venv/bin/activate
pip install -r requirements.txt

# Restart service
sudo systemctl restart streamlit-optimization.service

# Check status
sudo systemctl status streamlit-optimization.service
```

---

## 🛠️ Troubleshooting

### Issue: Service won't start

```bash
# Check logs
sudo journalctl -u streamlit-optimization.service -n 50

# Check if port is in use
sudo netstat -tulpn | grep 8501

# Verify .env file exists
ls -la /home/ec2-user/Optimization/.env
```

### Issue: Can't access from browser

1. **Check Security Group:**
   - Ensure port 80 is open in EC2 Security Group
   - Source: `0.0.0.0/0`

2. **Check Nginx:**
   ```bash
   sudo systemctl status nginx
   sudo nginx -t
   ```

3. **Check Streamlit:**
   ```bash
   sudo systemctl status streamlit-optimization.service
   curl http://localhost:8501
   ```

### Issue: Environment variables not loading

```bash
# Verify .env file
cat /home/ec2-user/Optimization/.env

# Check file permissions
ls -la /home/ec2-user/Optimization/.env

# Re-run setup script
cd /home/ec2-user/Optimization
./scripts/setup-from-github-secrets.sh
```

### Issue: Port 8501 already in use

```bash
# Find process using port 8501
sudo lsof -i :8501

# Kill the process (replace PID with actual process ID)
sudo kill -9 PID

# Or restart the service
sudo systemctl restart streamlit-optimization.service
```

---

## 📝 Useful Commands

### Service Management
```bash
# Start service
sudo systemctl start streamlit-optimization.service

# Stop service
sudo systemctl stop streamlit-optimization.service

# Restart service
sudo systemctl restart streamlit-optimization.service

# Check status
sudo systemctl status streamlit-optimization.service

# View logs
sudo journalctl -u streamlit-optimization.service -f
```

### Nginx Management
```bash
# Start nginx
sudo systemctl start nginx

# Stop nginx
sudo systemctl stop nginx

# Restart nginx
sudo systemctl restart nginx

# Reload nginx (without downtime)
sudo systemctl reload nginx

# Test configuration
sudo nginx -t
```

### View Logs
```bash
# Streamlit logs
sudo journalctl -u streamlit-optimization.service -n 100

# Nginx access logs
sudo tail -f /var/log/nginx/access.log

# Nginx error logs
sudo tail -f /var/log/nginx/error.log
```

---

## 🔒 Security Best Practices

1. **Firewall Configuration:**
   - Only open necessary ports (80, 443)
   - Restrict SSH access if possible

2. **Environment Variables:**
   - Never commit `.env` file
   - Use GitHub Secrets for sensitive data
   - Set proper file permissions: `chmod 600 .env`

3. **Regular Updates:**
   - Keep system packages updated
   - Update Python dependencies regularly
   - Monitor security advisories

4. **SSL/HTTPS (Recommended):**
   - Set up SSL certificate using Let's Encrypt
   - Configure HTTPS in nginx
   - Redirect HTTP to HTTPS

---

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review service logs
3. Verify all configuration files
4. Check EC2 Security Group settings

---

## ✅ Deployment Checklist

- [ ] EC2 instance running
- [ ] Python 3.10+ installed
- [ ] Nginx installed and configured
- [ ] Repository cloned
- [ ] GitHub Secrets configured
- [ ] `.env` file created
- [ ] Dependencies installed
- [ ] Systemd service configured
- [ ] Nginx configured with correct IP
- [ ] Security Group allows port 80
- [ ] Service running
- [ ] Application accessible at http://43.204.142.218/

---

**Deployment Date:** _______________  
**Deployed By:** _______________  
**Status:** _______________

