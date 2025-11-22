#!/bin/bash
# Wrapper script to start Streamlit with GitHub Secrets or .env file loaded as environment variables

cd /home/ec2-user/Optimization

# Try to load GitHub Secrets first
if [ -f "scripts/load-github-secrets.sh" ]; then
    source scripts/load-github-secrets.sh
fi

# Fallback: Load .env file if it exists (takes precedence if GitHub secrets failed)
if [ -f ".env" ]; then
    set -a
    source .env
    set +a
fi

# Start Streamlit with the loaded environment variables
exec /home/ec2-user/Optimization/.venv/bin/streamlit run src/dashboard.py \
    --server.port 8501 \
    --server.address 0.0.0.0 \
    --server.headless true \
    --server.runOnSave true \
    --browser.gatherUsageStats false

