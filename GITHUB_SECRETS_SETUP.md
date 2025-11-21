# GitHub Secrets Setup Guide

This guide will walk you through setting up GitHub Secrets for your project, so that anyone who clones the repository can deploy it on EC2 using GitHub Secrets instead of local `.env` files.

## 📋 Prerequisites

- A GitHub repository for this project
- GitHub account with admin access to the repository
- EC2 instance with GitHub CLI or access to GitHub API

---

## Step 1: Identify All Environment Variables

Based on the codebase, here are all the environment variables your project uses:

### Required Variables:
1. **AWS_ACCESS_KEY_ID** - Your AWS access key
2. **AWS_SECRET_ACCESS_KEY** - Your AWS secret key
3. **AWS_REGION** - AWS region (e.g., `us-east-2`)
4. **DB_HOST** - Database hostname
5. **DB_PORT** - Database port (usually `5432`)
6. **DB_NAME** - Database name
7. **DB_USER** - Database username
8. **DB_PASSWORD** - Database password

### Optional Variables:
9. **OPENAI_API_KEY** - For master model comparison (optional)
10. **DATABASE_URL** - Alternative to individual DB_* variables (full connection string)

---

## Step 2: Add Secrets to GitHub Repository

### Method 1: Using GitHub Web Interface (Recommended)

1. **Go to your GitHub repository**
   - Navigate to: `https://github.com/YOUR_USERNAME/YOUR_REPO_NAME`

2. **Open Settings**
   - Click on the **Settings** tab (top menu)

3. **Navigate to Secrets**
   - In the left sidebar, click **Secrets and variables** → **Actions**
   - Or go directly to: `https://github.com/YOUR_USERNAME/YOUR_REPO_NAME/settings/secrets/actions`

4. **Add each secret one by one:**
   - Click **New repository secret**
   - Enter the **Name** (exactly as listed below)
   - Enter the **Secret** value
   - Click **Add secret**

   **Add these secrets in this order:**

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
   DATABASE_URL (optional - if you prefer full connection string)
   ```

### Method 2: Using GitHub CLI

If you have GitHub CLI installed, you can add secrets from the command line:

```bash
# Install GitHub CLI if not installed
# Windows: winget install GitHub.cli
# Mac: brew install gh
# Linux: sudo apt install gh

# Authenticate
gh auth login

# Add secrets (replace values with your actual values)
gh secret set AWS_ACCESS_KEY_ID --body "your_access_key_here"
gh secret set AWS_SECRET_ACCESS_KEY --body "your_secret_key_here"
gh secret set AWS_REGION --body "us-east-2"
gh secret set DB_HOST --body "your_db_host_here"
gh secret set DB_PORT --body "5432"
gh secret set DB_NAME --body "bellatrix_db"
gh secret set DB_USER --body "postgres"
gh secret set DB_PASSWORD --body "your_db_password_here"
gh secret set OPENAI_API_KEY --body "your_openai_key_here"  # Optional
```

---

## Step 3: Verify Secrets Are Added

1. Go back to **Settings** → **Secrets and variables** → **Actions**
2. You should see all your secrets listed (values will be hidden with dots)
3. Make sure all required secrets are present

---

## Step 4: Set Up GitHub Actions Workflow (Optional - for CI/CD)

If you want to use GitHub Actions for automated deployment, the workflow file (`.github/workflows/deploy.yml`) will automatically use these secrets.

---

## Step 5: Deploy on EC2 Using Secrets

### Option A: Using the EC2 Setup Script (Recommended)

1. **SSH into your EC2 instance:**
   ```bash
   ssh -i your-key.pem ec2-user@your-ec2-ip
   ```

2. **Clone the repository:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
   cd YOUR_REPO_NAME
   ```

3. **Run the setup script:**
   ```bash
   chmod +x scripts/setup-from-github-secrets.sh
   ./scripts/setup-from-github-secrets.sh
   ```

   This script will:
   - Install GitHub CLI if needed
   - Authenticate with GitHub
   - Download all secrets from GitHub
   - Create a `.env` file with all the secrets
   - Set up the project

### Option B: Manual Setup on EC2

1. **Install GitHub CLI on EC2:**
   ```bash
   # Amazon Linux 2
   sudo yum install -y gh
   
   # Ubuntu
   curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
   echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
   sudo apt update
   sudo apt install gh
   ```

2. **Authenticate with GitHub:**
   ```bash
   gh auth login
   # Follow the prompts to authenticate
   ```

3. **Clone your repository:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
   cd YOUR_REPO_NAME
   ```

4. **Create .env file from GitHub Secrets:**
   ```bash
   # Create .env file
   cat > .env << EOF
   AWS_ACCESS_KEY_ID=$(gh secret get AWS_ACCESS_KEY_ID)
   AWS_SECRET_ACCESS_KEY=$(gh secret get AWS_SECRET_ACCESS_KEY)
   AWS_REGION=$(gh secret get AWS_REGION)
   DB_HOST=$(gh secret get DB_HOST)
   DB_PORT=$(gh secret get DB_PORT)
   DB_NAME=$(gh secret get DB_NAME)
   DB_USER=$(gh secret get DB_USER)
   DB_PASSWORD=$(gh secret get DB_PASSWORD)
   OPENAI_API_KEY=$(gh secret get OPENAI_API_KEY 2>/dev/null || echo "")
   EOF
   ```

5. **Set up the project:**
   ```bash
   python3 setup.py
   ```

6. **Start the application:**
   ```bash
   ./start_dashboard.sh
   ```

---

## Step 6: Security Best Practices

1. **Never commit `.env` files:**
   - Make sure `.env` is in your `.gitignore`
   - Verify it's not tracked: `git ls-files | grep .env`

2. **Use least privilege:**
   - Create AWS IAM users with minimal required permissions
   - Use separate credentials for different environments (dev/staging/prod)

3. **Rotate secrets regularly:**
   - Update secrets in GitHub when credentials change
   - Update the `.env` file on EC2 after rotating secrets

4. **Use IAM Roles on EC2 (Advanced):**
   - Instead of access keys, consider using EC2 IAM roles
   - This eliminates the need for AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY

---

## Troubleshooting

### Issue: "gh: command not found"
**Solution:** Install GitHub CLI (see Step 5, Option B)

### Issue: "gh auth login" fails
**Solution:** 
- Make sure you have internet access on EC2
- Try using a personal access token instead:
  ```bash
  gh auth login --with-token < token.txt
  ```

### Issue: "Secret not found"
**Solution:**
- Verify the secret name matches exactly (case-sensitive)
- Check that you're authenticated with the correct GitHub account
- Ensure you have access to the repository

### Issue: ".env file not created"
**Solution:**
- Check file permissions: `ls -la .env`
- Verify GitHub CLI is working: `gh secret list`
- Manually create the file if needed

---

## Quick Reference: Secret Names

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

## Next Steps

After setting up secrets:
1. ✅ Test the deployment on EC2
2. ✅ Verify the application works correctly
3. ✅ Update your team documentation
4. ✅ Share this guide with team members

---

## Need Help?

If you encounter any issues:
1. Check the troubleshooting section above
2. Review GitHub Secrets documentation: https://docs.github.com/en/actions/security-guides/encrypted-secrets
3. Verify all secrets are correctly named and have values

