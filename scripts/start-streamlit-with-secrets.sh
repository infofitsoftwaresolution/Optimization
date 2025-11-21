#!/bin/bash
# Wrapper script to start Streamlit with GitHub Secrets loaded as environment variables

cd /home/ec2-user/Optimization

# Load GitHub Secrets as environment variables
source scripts/load-github-secrets.sh

# Start Streamlit with the loaded environment variables
exec /home/ec2-user/Optimization/.venv/bin/streamlit run src/dashboard.py \
    --server.port 8501 \
    --server.address 0.0.0.0 \
    --server.headless true \
    --server.runOnSave true \
    --browser.gatherUsageStats false

