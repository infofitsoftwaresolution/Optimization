#!/bin/bash
# Linux/Mac shell script to start the dashboard
# This script activates the virtual environment and starts Streamlit

echo "========================================"
echo "Starting AI Cost Optimizer Dashboard..."
echo "========================================"
echo ""

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "[ERROR] Virtual environment not found!"
    echo ""
    echo "Please run the setup first:"
    echo "  python3 setup.py"
    echo ""
    echo "This will automatically:"
    echo "  - Create virtual environment"
    echo "  - Install all dependencies"
    echo "  - Set up configuration files"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "[WARNING] .env file not found!"
    echo ""
    echo "Please create .env file with your AWS credentials:"
    echo "  1. Copy .env.example to .env: cp .env.example .env"
    echo "  2. Edit .env and add your AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY"
    echo ""
    echo "Or run setup.py which will create it automatically."
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Check if dependencies are installed
python -c "import streamlit" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "[WARNING] Dependencies not installed!"
    echo "Installing dependencies..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "[ERROR] Failed to install dependencies!"
        exit 1
    fi
fi

# Set environment variable to skip Streamlit email prompt
export STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Start Streamlit dashboard
echo ""
echo "========================================"
echo "Starting Streamlit dashboard..."
echo "========================================"
echo ""
echo "The dashboard will be available at: http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the server."
echo ""
streamlit run src/dashboard.py
