#!/bin/bash
# Script to load GitHub Secrets as environment variables
# This is sourced by the systemd service

# Check if GitHub CLI is available
if ! command -v gh &> /dev/null; then
    echo "GitHub CLI not found. Falling back to .env file if exists."
    if [ -f "/home/ec2-user/Optimization/.env" ]; then
        set -a
        source /home/ec2-user/Optimization/.env
        set +a
    fi
    return 0
fi

# Check if authenticated
if ! gh auth status &> /dev/null; then
    echo "Not authenticated with GitHub. Falling back to .env file if exists."
    if [ -f "/home/ec2-user/Optimization/.env" ]; then
        set -a
        source /home/ec2-user/Optimization/.env
        set +a
    fi
    return 0
fi

# Function to get secret or return empty string
get_secret() {
    local secret_name=$1
    gh secret get "$secret_name" 2>/dev/null || echo ""
}

# Load secrets as environment variables
export AWS_ACCESS_KEY_ID=$(get_secret "AWS_ACCESS_KEY_ID")
export AWS_SECRET_ACCESS_KEY=$(get_secret "AWS_SECRET_ACCESS_KEY")
export AWS_REGION=$(get_secret "AWS_REGION")
export DB_HOST=$(get_secret "DB_HOST")
export DB_PORT=$(get_secret "DB_PORT")
export DB_NAME=$(get_secret "DB_NAME")
export DB_USER=$(get_secret "DB_USER")
export DB_PASSWORD=$(get_secret "DB_PASSWORD")
export OPENAI_API_KEY=$(get_secret "OPENAI_API_KEY")
export STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# If DATABASE_URL is set, use it
DATABASE_URL_SECRET=$(get_secret "DATABASE_URL")
if [ -n "$DATABASE_URL_SECRET" ]; then
    export DATABASE_URL="$DATABASE_URL_SECRET"
fi

