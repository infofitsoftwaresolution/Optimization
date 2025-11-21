# PowerShell script to set up the project on Windows using GitHub Secrets
# This script downloads secrets from GitHub and creates a .env file

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setting up project from GitHub Secrets" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if GitHub CLI is installed
if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    Write-Host "GitHub CLI not found. Installing..." -ForegroundColor Yellow
    
    # Check if winget is available
    if (Get-Command winget -ErrorAction SilentlyContinue) {
        Write-Host "Installing GitHub CLI using winget..." -ForegroundColor Yellow
        winget install --id GitHub.cli -e
    } else {
        Write-Host "Please install GitHub CLI manually:" -ForegroundColor Red
        Write-Host "  Visit: https://cli.github.com/manual/installation" -ForegroundColor Red
        Write-Host "  Or use: winget install --id GitHub.cli" -ForegroundColor Red
        exit 1
    }
}

Write-Host "GitHub CLI is installed." -ForegroundColor Green
Write-Host ""

# Check if authenticated
try {
    gh auth status 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw "Not authenticated"
    }
} catch {
    Write-Host "Not authenticated with GitHub. Please authenticate..." -ForegroundColor Yellow
    Write-Host "You'll need to authenticate with GitHub."
    Write-Host "Options:"
    Write-Host "  1. Interactive login (recommended): gh auth login"
    Write-Host "  2. Use token: gh auth login --with-token < token.txt"
    Write-Host ""
    Read-Host "Press Enter to start authentication"
    gh auth login
}

Write-Host "Authenticated with GitHub." -ForegroundColor Green
Write-Host ""

# Get repository info
$remoteUrl = git remote get-url origin 2>$null
if (-not $remoteUrl) {
    Write-Host "Could not detect repository. Please run this script from the repository root." -ForegroundColor Red
    exit 1
}

$repoMatch = $remoteUrl -match 'github\.com[:/]([^/]+)/([^/]+)(\.git)?$'
if (-not $repoMatch) {
    Write-Host "Could not parse repository URL. Please ensure you're in a git repository." -ForegroundColor Red
    exit 1
}

$repoOwner = $matches[1]
$repoName = $matches[2] -replace '\.git$', ''

Write-Host "Repository: $repoOwner/$repoName" -ForegroundColor Cyan
Write-Host ""

# Function to get secret or return empty string
function Get-GitHubSecret {
    param([string]$SecretName)
    try {
        $value = gh secret get $SecretName 2>$null
        return $value
    } catch {
        return ""
    }
}

# Check if secrets exist
Write-Host "Checking for required secrets..." -ForegroundColor Cyan
$requiredSecrets = @(
    "AWS_ACCESS_KEY_ID",
    "AWS_SECRET_ACCESS_KEY",
    "AWS_REGION",
    "DB_HOST",
    "DB_PORT",
    "DB_NAME",
    "DB_USER",
    "DB_PASSWORD"
)

$missingSecrets = @()

foreach ($secret in $requiredSecrets) {
    $value = Get-GitHubSecret -SecretName $secret
    if ([string]::IsNullOrWhiteSpace($value)) {
        $missingSecrets += $secret
    }
}

if ($missingSecrets.Count -gt 0) {
    Write-Host "Missing required secrets:" -ForegroundColor Red
    foreach ($secret in $missingSecrets) {
        Write-Host "  - $secret" -ForegroundColor Red
    }
    Write-Host ""
    Write-Host "Please add these secrets to your GitHub repository:" -ForegroundColor Yellow
    Write-Host "  https://github.com/$repoOwner/$repoName/settings/secrets/actions" -ForegroundColor Yellow
    exit 1
}

Write-Host "All required secrets found." -ForegroundColor Green
Write-Host ""

# Create .env file
$envFile = ".env"
Write-Host "Creating $envFile file from GitHub Secrets..." -ForegroundColor Cyan

# Backup existing .env if it exists
if (Test-Path $envFile) {
    Write-Host "Backing up existing .env file to .env.backup" -ForegroundColor Yellow
    Copy-Item $envFile "${envFile}.backup"
}

# Get secret values
$awsAccessKey = Get-GitHubSecret -SecretName "AWS_ACCESS_KEY_ID"
$awsSecretKey = Get-GitHubSecret -SecretName "AWS_SECRET_ACCESS_KEY"
$awsRegion = Get-GitHubSecret -SecretName "AWS_REGION"
$dbHost = Get-GitHubSecret -SecretName "DB_HOST"
$dbPort = Get-GitHubSecret -SecretName "DB_PORT"
$dbName = Get-GitHubSecret -SecretName "DB_NAME"
$dbUser = Get-GitHubSecret -SecretName "DB_USER"
$dbPassword = Get-GitHubSecret -SecretName "DB_PASSWORD"
$openaiKey = Get-GitHubSecret -SecretName "OPENAI_API_KEY"

# Write .env file
$envContent = @"
# AWS Configuration
# Generated from GitHub Secrets on $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
AWS_ACCESS_KEY_ID=$awsAccessKey
AWS_SECRET_ACCESS_KEY=$awsSecretKey
AWS_REGION=$awsRegion

# Database Configuration
DB_HOST=$dbHost
DB_PORT=$dbPort
DB_NAME=$dbName
DB_USER=$dbUser
DB_PASSWORD=$dbPassword

# OpenAI API Key (Optional)
"@

if (-not [string]::IsNullOrWhiteSpace($openaiKey)) {
    $envContent += "OPENAI_API_KEY=$openaiKey`n"
} else {
    $envContent += "# OPENAI_API_KEY=your_openai_api_key_here`n"
}

$envContent += @"

# Streamlit Configuration
STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
"@

$envContent | Out-File -FilePath $envFile -Encoding utf8 -NoNewline

# Set file permissions (Windows)
$acl = Get-Acl $envFile
$accessRule = New-Object System.Security.AccessControl.FileSystemAccessRule(
    $env:USERNAME,
    "FullControl",
    "Allow"
)
$acl.SetAccessRule($accessRule)
Set-Acl $envFile $acl

Write-Host "✓ Created $envFile file" -ForegroundColor Green
Write-Host ""

# Verify .env file was created
if (-not (Test-Path $envFile)) {
    Write-Host "Error: Failed to create .env file" -ForegroundColor Red
    exit 1
}

# Check if setup.py exists and run it
if (Test-Path "setup.py") {
    Write-Host "Running project setup..." -ForegroundColor Cyan
    python setup.py
} else {
    Write-Host "setup.py not found. Skipping automated setup." -ForegroundColor Yellow
    Write-Host "Please run the setup manually:"
    Write-Host "  1. Create virtual environment: python -m venv .venv"
    Write-Host "  2. Activate it: .venv\Scripts\Activate.ps1"
    Write-Host "  3. Install dependencies: pip install -r requirements.txt"
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setup complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:"
Write-Host "  1. Verify .env file: Get-Content .env (check that values are correct)"
Write-Host "  2. Start the dashboard: .\start_dashboard.bat"
Write-Host ""
Write-Host "Note: The .env file contains sensitive information."
Write-Host "      Make sure it's in .gitignore and never commit it!" -ForegroundColor Yellow

