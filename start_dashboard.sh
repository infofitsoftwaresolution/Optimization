#!/bin/bash
# Production startup script for AWS EC2
# Usage: ./start_dashboard.sh

echo "=== Starting AI Cost Optimizer Dashboard ==="
echo ""

# Change to project directory
cd "$(dirname "$0")"

# Check Python installation
echo "Checking Python installation..."
python3 --version || python --version

# Install/upgrade required packages
echo "Installing required packages..."
pip3 install -r requirements.txt --upgrade || pip install -r requirements.txt --upgrade

# Clear Streamlit cache
echo "Clearing Streamlit cache..."
python3 -m streamlit cache clear 2>/dev/null || python -m streamlit cache clear 2>/dev/null

# Check for existing processes on port 8501
echo "Checking port 8501..."
if lsof -Pi :8501 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "Port 8501 is in use. Attempting to free it..."
    kill -9 $(lsof -ti:8501) 2>/dev/null
    sleep 2
fi

# Start Streamlit server
echo ""
echo "Starting Streamlit server..."
echo "Dashboard will be available at: http://localhost:8501"
echo ""
echo "To run in background: nohup ./start_dashboard.sh > dashboard.log 2>&1 &"
echo ""

# Run Streamlit (use python3 if available, else python)
python3 -m streamlit run src/dashboard.py --server.port 8501 --server.address 0.0.0.0 || \
python -m streamlit run src/dashboard.py --server.port 8501 --server.address 0.0.0.0

