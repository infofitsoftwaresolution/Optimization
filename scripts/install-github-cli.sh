#!/bin/bash
# Install GitHub CLI on Amazon Linux 2

set -e

echo "Installing GitHub CLI for Amazon Linux 2..."

# Check if already installed
if command -v gh &> /dev/null; then
    echo "GitHub CLI is already installed: $(gh --version)"
    exit 0
fi

# Download and install GitHub CLI
cd /tmp

# For Amazon Linux 2, we need to download the RPM
echo "Downloading GitHub CLI..."
curl -fsSL https://github.com/cli/cli/releases/latest/download/gh_$(curl -s https://api.github.com/repos/cli/cli/releases/latest | grep tag_name | cut -d '"' -f 4 | cut -d 'v' -f 2)_linux_amd64.tar.gz -o gh.tar.gz

# Extract
tar -xzf gh.tar.gz

# Install
sudo mv gh_*_linux_amd64/bin/gh /usr/local/bin/
sudo chmod +x /usr/local/bin/gh

# Cleanup
rm -rf gh_*_linux_amd64 gh.tar.gz

# Verify installation
if command -v gh &> /dev/null; then
    echo "✅ GitHub CLI installed successfully: $(gh --version)"
else
    echo "❌ GitHub CLI installation failed"
    exit 1
fi

