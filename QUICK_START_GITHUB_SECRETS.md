# Quick Start: GitHub Secrets Setup

## 🚀 Quick Setup (5 Minutes)

### Step 1: Add Secrets to GitHub (2 minutes)

1. Go to: `https://github.com/YOUR_USERNAME/YOUR_REPO/settings/secrets/actions`
2. Click **"New repository secret"** for each:

   ```
   AWS_ACCESS_KEY_ID
   AWS_SECRET_ACCESS_KEY
   AWS_REGION
   DB_HOST
   DB_PORT
   DB_NAME
   DB_USER
   DB_PASSWORD
   OPENAI_API_KEY (optional)
   ```

### Step 2: On EC2 (3 minutes)

```bash
# 1. Clone repository
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO

# 2. Run setup script
chmod +x scripts/setup-from-github-secrets.sh
./scripts/setup-from-github-secrets.sh

# 3. Start the app
./start_dashboard.sh
```

**That's it!** The script will:
- ✅ Install GitHub CLI
- ✅ Authenticate with GitHub
- ✅ Download all secrets
- ✅ Create `.env` file automatically
- ✅ Set up the project

---

## 📋 Complete Secret List

Copy-paste this list when adding secrets:

```
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
AWS_REGION
DB_HOST
DB_PORT
DB_NAME
DB_USER
DB_PASSWORD
OPENAI_API_KEY
```

---

## 🔍 Troubleshooting

**"gh: command not found"**
→ The script will install it automatically, or install manually:
```bash
# Amazon Linux
sudo yum install -y gh

# Ubuntu
sudo apt install gh
```

**"Not authenticated"**
→ Run: `gh auth login` and follow prompts

**"Secret not found"**
→ Double-check secret names (case-sensitive) in GitHub Settings

---

## 📖 Full Documentation

For detailed instructions, see: [GITHUB_SECRETS_SETUP.md](GITHUB_SECRETS_SETUP.md)

