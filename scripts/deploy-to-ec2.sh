#!/bin/bash
# Complete deployment script for EC2
# This script handles the entire deployment process

set -e

EC2_IP="43.204.142.218"
PROJECT_DIR="/home/ec2-user/Optimization"

echo "========================================"
echo "🚀 Deploying to EC2: $EC2_IP"
echo "========================================"
echo ""

# Check if we're on EC2
if [ ! -d "$PROJECT_DIR" ]; then
    echo "❌ Error: Project directory not found: $PROJECT_DIR"
    echo "   This script should be run on the EC2 instance."
    echo "   Please SSH into EC2 first: ssh -i your-key.pem ec2-user@$EC2_IP"
    exit 1
fi

cd "$PROJECT_DIR"

# Step 1: Pull latest code
echo "📥 Step 1: Pulling latest code from GitHub..."
git fetch origin
git reset --hard origin/main
echo "✅ Code updated"
echo ""

# Step 2: Set up environment from GitHub Secrets
echo "🔐 Step 2: Setting up environment from GitHub Secrets..."
if [ -f "scripts/setup-from-github-secrets.sh" ]; then
    chmod +x scripts/setup-from-github-secrets.sh
    ./scripts/setup-from-github-secrets.sh || {
        echo "⚠️  Warning: GitHub Secrets setup failed. Using existing .env file if available."
    }
else
    echo "⚠️  Warning: setup-from-github-secrets.sh not found. Skipping..."
fi
echo ""

# Step 3: Set up virtual environment
echo "🐍 Step 3: Setting up Python virtual environment..."
if [ ! -d ".venv" ]; then
    python3.10 -m venv .venv || python3 -m venv .venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

source .venv/bin/activate
echo "✅ Virtual environment activated"
echo ""

# Step 4: Install/update dependencies
echo "📦 Step 4: Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Dependencies installed"
echo ""

# Step 5: Configure Nginx
echo "🌐 Step 5: Configuring Nginx..."
if [ -f "nginx-optimization-app.conf" ]; then
    sudo cp nginx-optimization-app.conf /etc/nginx/conf.d/optimization-app.conf
    sudo nginx -t && {
        sudo systemctl restart nginx
        sudo systemctl enable nginx
        echo "✅ Nginx configured and restarted"
    } || {
        echo "⚠️  Warning: Nginx configuration test failed"
    }
else
    echo "⚠️  Warning: nginx-optimization-app.conf not found"
fi
echo ""

# Step 6: Set up systemd service
echo "⚙️  Step 6: Setting up systemd service..."
if [ -f "streamlit-optimization.service" ]; then
    sudo cp streamlit-optimization.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable streamlit-optimization.service
    echo "✅ Systemd service configured"
else
    echo "⚠️  Warning: streamlit-optimization.service not found"
fi
echo ""

# Step 7: Restart Streamlit service
echo "🔄 Step 7: Restarting Streamlit service..."
sudo systemctl restart streamlit-optimization.service
sleep 5
echo "✅ Service restarted"
echo ""

# Step 8: Health check
echo "🏥 Step 8: Performing health check..."
for i in {1..10}; do
    if curl -f -s --max-time 5 http://localhost:8501/ > /dev/null 2>&1; then
        echo "✅ Health check passed - App is responding"
        break
    fi
    if [ $i -eq 10 ]; then
        echo "❌ Health check failed after 10 attempts"
        echo "   Checking service status..."
        sudo systemctl status streamlit-optimization.service --no-pager -l
        exit 1
    fi
    echo "   Attempt $i/10 failed, retrying..."
    sleep 5
done
echo ""

# Step 9: Final status
echo "========================================"
echo "✅ Deployment completed successfully!"
echo "========================================"
echo ""
echo "🌐 Application URL: http://$EC2_IP/"
echo ""
echo "📊 Service Status:"
sudo systemctl status streamlit-optimization.service --no-pager -l | head -10
echo ""
echo "📝 Useful commands:"
echo "   View logs:    sudo journalctl -u streamlit-optimization.service -f"
echo "   Restart:      sudo systemctl restart streamlit-optimization.service"
echo "   Status:       sudo systemctl status streamlit-optimization.service"
echo ""

