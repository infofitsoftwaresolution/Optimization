#!/bin/bash
# Script to update the live site on EC2
# Run this on the EC2 instance to pull latest changes and restart services

set -e

PROJECT_DIR="/home/ec2-user/Optimization"

echo "========================================"
echo "🔄 Updating Live Site"
echo "========================================"
echo ""

# Check if we're in the right directory
if [ ! -d "$PROJECT_DIR" ]; then
    echo "❌ Error: Project directory not found: $PROJECT_DIR"
    echo "   Please run this script from the EC2 instance"
    exit 1
fi

cd "$PROJECT_DIR"

# Step 1: Pull latest code
echo "📥 Step 1: Pulling latest code from GitHub..."
git fetch origin
git pull origin main
echo "✅ Code updated"
echo ""

# Step 2: Check current commit
echo "📝 Current commit:"
git log -1 --oneline
echo ""

# Step 3: Update environment if needed
echo "🔐 Step 3: Updating environment variables..."
if [ -f "scripts/setup-from-github-secrets.sh" ]; then
    # Only update if .env doesn't exist or is older than 1 day
    if [ ! -f ".env" ] || [ "scripts/setup-from-github-secrets.sh" -nt ".env" ]; then
        echo "   Updating .env from GitHub Secrets..."
        chmod +x scripts/setup-from-github-secrets.sh
        ./scripts/setup-from-github-secrets.sh || echo "   ⚠️  Warning: Could not update from GitHub Secrets"
    else
        echo "   .env file is up to date"
    fi
fi
echo ""

# Step 4: Activate virtual environment and update dependencies
echo "📦 Step 4: Updating dependencies..."
if [ -d ".venv" ]; then
    source .venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    echo "✅ Dependencies updated"
else
    echo "⚠️  Warning: Virtual environment not found. Creating..."
    python3.10 -m venv .venv || python3 -m venv .venv
    source .venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    echo "✅ Virtual environment created and dependencies installed"
fi
echo ""

# Step 5: Restart Streamlit service
echo "🔄 Step 5: Restarting Streamlit service..."
sudo systemctl restart streamlit-optimization.service
sleep 5
echo "✅ Service restarted"
echo ""

# Step 6: Check service status
echo "📊 Step 6: Checking service status..."
if sudo systemctl is-active --quiet streamlit-optimization.service; then
    echo "✅ Service is running"
else
    echo "❌ Service is not running!"
    echo "   Checking logs..."
    sudo journalctl -u streamlit-optimization.service -n 20 --no-pager
    exit 1
fi
echo ""

# Step 7: Health check
echo "🏥 Step 7: Performing health check..."
for i in {1..5}; do
    if curl -f -s --max-time 5 http://localhost:8501/ > /dev/null 2>&1; then
        echo "✅ Health check passed - App is responding"
        break
    fi
    if [ $i -eq 5 ]; then
        echo "⚠️  Health check failed - but service is running"
        echo "   This might be normal if the app is still starting up"
    else
        echo "   Attempt $i/5 failed, retrying..."
        sleep 3
    fi
done
echo ""

# Step 8: Restart Nginx (to clear any caches)
echo "🌐 Step 8: Restarting Nginx..."
sudo systemctl restart nginx
echo "✅ Nginx restarted"
echo ""

# Step 9: Final status
echo "========================================"
echo "✅ Update completed!"
echo "========================================"
echo ""
echo "🌐 Application URL: http://43.204.142.218/"
echo ""
echo "📊 Service Status:"
sudo systemctl status streamlit-optimization.service --no-pager -l | head -15
echo ""
echo "💡 If changes are not visible:"
echo "   1. Clear browser cache (Ctrl+Shift+R or Cmd+Shift+R)"
echo "   2. Try incognito/private browsing mode"
echo "   3. Check logs: sudo journalctl -u streamlit-optimization.service -f"
echo ""

