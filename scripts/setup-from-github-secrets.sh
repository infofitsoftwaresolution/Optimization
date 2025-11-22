#!/bin/bash
# Script to set up the project on EC2 using GitHub Secrets
# This script downloads secrets from GitHub and creates a .env file

set -e  # Exit on error

echo "========================================"
echo "Setting up project from GitHub Secrets"
echo "========================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if GitHub CLI is installed
if ! command -v gh &> /dev/null; then
    echo -e "${YELLOW}GitHub CLI not found. Installing...${NC}"
    
    # Detect OS and install accordingly
    if [ -f /etc/redhat-release ]; then
        # Amazon Linux / CentOS / RHEL
        echo "Detected Amazon Linux / CentOS / RHEL"
        # Try using the install script
        if [ -f "scripts/install-github-cli.sh" ]; then
            chmod +x scripts/install-github-cli.sh
            ./scripts/install-github-cli.sh || {
                echo -e "${YELLOW}Install script failed, trying yum...${NC}"
                sudo yum install -y gh || {
                    echo -e "${RED}Failed to install GitHub CLI. Please install manually.${NC}"
                    echo "Visit: https://cli.github.com/manual/installation"
                    exit 1
                }
            }
        else
            sudo yum install -y gh || {
                echo -e "${RED}Failed to install GitHub CLI. Please install manually.${NC}"
                echo "Visit: https://cli.github.com/manual/installation"
                exit 1
            }
        fi
    elif [ -f /etc/debian_version ]; then
        # Debian / Ubuntu
        echo "Detected Debian / Ubuntu"
        curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
        echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
        sudo apt update
        sudo apt install -y gh
    else
        echo -e "${RED}Unsupported OS. Please install GitHub CLI manually.${NC}"
        echo "Visit: https://cli.github.com/manual/installation"
        exit 1
    fi
fi

echo -e "${GREEN}GitHub CLI is installed.${NC}"
echo ""

# Check if authenticated
if ! gh auth status &> /dev/null; then
    echo -e "${YELLOW}Not authenticated with GitHub. Please authenticate...${NC}"
    echo "You'll need to authenticate with GitHub."
    echo "Options:"
    echo "  1. Interactive login (recommended): gh auth login"
    echo "  2. Use token: gh auth login --with-token < token.txt"
    echo ""
    read -p "Press Enter to start authentication..."
    gh auth login
fi

echo -e "${GREEN}Authenticated with GitHub.${NC}"
echo ""

# Get repository info
REPO_OWNER=$(git remote get-url origin 2>/dev/null | sed -E 's/.*github.com[:/]([^/]+)\/([^/]+)(\.git)?$/\1/' || echo "")
REPO_NAME=$(git remote get-url origin 2>/dev/null | sed -E 's/.*github.com[:/]([^/]+)\/([^/]+)(\.git)?$/\2/' | sed 's/\.git$//' || echo "")

if [ -z "$REPO_OWNER" ] || [ -z "$REPO_NAME" ]; then
    echo -e "${RED}Could not detect repository. Please run this script from the repository root.${NC}"
    exit 1
fi

echo "Repository: $REPO_OWNER/$REPO_NAME"
echo ""

# Function to get secret or return empty string
get_secret() {
    local secret_name=$1
    local value=$(gh secret get "$secret_name" 2>/dev/null || echo "")
    echo "$value"
}

# Check if secrets exist
echo "Checking for required secrets..."
REQUIRED_SECRETS=("AWS_ACCESS_KEY_ID" "AWS_SECRET_ACCESS_KEY" "AWS_REGION" "DB_HOST" "DB_PORT" "DB_NAME" "DB_USER" "DB_PASSWORD")
MISSING_SECRETS=()

for secret in "${REQUIRED_SECRETS[@]}"; do
    if [ -z "$(get_secret "$secret")" ]; then
        MISSING_SECRETS+=("$secret")
    fi
done

if [ ${#MISSING_SECRETS[@]} -gt 0 ]; then
    echo -e "${RED}Missing required secrets:${NC}"
    for secret in "${MISSING_SECRETS[@]}"; do
        echo "  - $secret"
    done
    echo ""
    echo "Please add these secrets to your GitHub repository:"
    echo "  https://github.com/$REPO_OWNER/$REPO_NAME/settings/secrets/actions"
    exit 1
fi

echo -e "${GREEN}All required secrets found.${NC}"
echo ""

# Create .env file
ENV_FILE=".env"
echo "Creating $ENV_FILE file from GitHub Secrets..."

# Backup existing .env if it exists
if [ -f "$ENV_FILE" ]; then
    echo -e "${YELLOW}Backing up existing .env file to .env.backup${NC}"
    cp "$ENV_FILE" "${ENV_FILE}.backup"
fi

# Write .env file
cat > "$ENV_FILE" << EOF
# AWS Configuration
# Generated from GitHub Secrets on $(date)
AWS_ACCESS_KEY_ID=$(get_secret "AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY=$(get_secret "AWS_SECRET_ACCESS_KEY")
AWS_REGION=$(get_secret "AWS_REGION")

# Database Configuration
DB_HOST=$(get_secret "DB_HOST")
DB_PORT=$(get_secret "DB_PORT")
DB_NAME=$(get_secret "DB_NAME")
DB_USER=$(get_secret "DB_USER")
DB_PASSWORD=$(get_secret "DB_PASSWORD")

# OpenAI API Key (Optional)
EOF

# Add optional secrets
OPENAI_KEY=$(get_secret "OPENAI_API_KEY")
if [ -n "$OPENAI_KEY" ]; then
    echo "OPENAI_API_KEY=$OPENAI_KEY" >> "$ENV_FILE"
else
    echo "# OPENAI_API_KEY=your_openai_api_key_here" >> "$ENV_FILE"
fi

# Add Streamlit config
cat >> "$ENV_FILE" << EOF

# Streamlit Configuration
STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
EOF

# Set proper permissions
chmod 600 "$ENV_FILE"

echo -e "${GREEN}✓ Created $ENV_FILE file${NC}"
echo ""

# Verify .env file was created
if [ ! -f "$ENV_FILE" ]; then
    echo -e "${RED}Error: Failed to create .env file${NC}"
    exit 1
fi

# Check if setup.py exists and run it
if [ -f "setup.py" ]; then
    echo "Running project setup..."
    python3 setup.py
else
    echo -e "${YELLOW}setup.py not found. Skipping automated setup.${NC}"
    echo "Please run the setup manually:"
    echo "  1. Create virtual environment: python3 -m venv .venv"
    echo "  2. Activate it: source .venv/bin/activate"
    echo "  3. Install dependencies: pip install -r requirements.txt"
fi

echo ""
echo "========================================"
echo -e "${GREEN}Setup complete!${NC}"
echo "========================================"
echo ""
echo "Next steps:"
echo "  1. Verify .env file: cat .env (check that values are correct)"
echo "  2. Start the dashboard: ./start_dashboard.sh"
echo ""
echo "Note: The .env file contains sensitive information."
echo "      Make sure it's in .gitignore and never commit it!"

