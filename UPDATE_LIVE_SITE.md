# How to Update the Live Site

If your changes are not showing on the hosted site at `http://43.204.142.218/`, follow these steps:

## 🚀 Quick Update (Recommended)

SSH into your EC2 instance and run:

```bash
cd /home/ec2-user/Optimization
chmod +x scripts/update-live-site.sh
./scripts/update-live-site.sh
```

This script will:
1. Pull latest code from GitHub
2. Update dependencies
3. Restart the Streamlit service
4. Restart Nginx
5. Perform health checks

---

## 🔍 Check Current Status

First, check what's happening:

```bash
cd /home/ec2-user/Optimization
chmod +x scripts/check-deployment-status.sh
./scripts/check-deployment-status.sh
```

This will show you:
- Git status (if code is up to date)
- Service status
- Port status
- Recent logs
- Any issues

---

## 📋 Manual Update Steps

If the script doesn't work, do it manually:

### Step 1: SSH into EC2
```bash
ssh -i your-key.pem ec2-user@43.204.142.218
```

### Step 2: Navigate to project
```bash
cd /home/ec2-user/Optimization
```

### Step 3: Pull latest code
```bash
git fetch origin
git pull origin main
```

### Step 4: Check what changed
```bash
git log -1 --oneline
```

### Step 5: Update dependencies (if needed)
```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### Step 6: Restart Streamlit service
```bash
sudo systemctl restart streamlit-optimization.service
```

### Step 7: Check service status
```bash
sudo systemctl status streamlit-optimization.service
```

### Step 8: Restart Nginx (clear cache)
```bash
sudo systemctl restart nginx
```

### Step 9: Test locally
```bash
curl http://localhost:8501
```

---

## 🐛 Troubleshooting

### Issue: Changes still not showing

1. **Clear browser cache:**
   - Press `Ctrl+Shift+R` (Windows/Linux) or `Cmd+Shift+R` (Mac)
   - Or use incognito/private browsing mode

2. **Check if service restarted:**
   ```bash
   sudo systemctl status streamlit-optimization.service
   ```

3. **Check logs for errors:**
   ```bash
   sudo journalctl -u streamlit-optimization.service -n 50
   ```

4. **Verify code was pulled:**
   ```bash
   cd /home/ec2-user/Optimization
   git log -1 --oneline
   ```

5. **Force restart everything:**
   ```bash
   sudo systemctl stop streamlit-optimization.service
   sleep 2
   sudo systemctl start streamlit-optimization.service
   sudo systemctl restart nginx
   ```

### Issue: Service won't start

```bash
# Check logs
sudo journalctl -u streamlit-optimization.service -n 50

# Check if port is in use
sudo lsof -i :8501

# Check if virtual environment exists
ls -la /home/ec2-user/Optimization/.venv

# Check if streamlit is installed
/home/ec2-user/Optimization/.venv/bin/streamlit --version
```

### Issue: Code not pulling from GitHub

```bash
# Check git remote
git remote -v

# Check if you're on the right branch
git branch

# Force pull
git fetch origin
git reset --hard origin/main
```

### Issue: Environment variables not loading

```bash
# Re-run setup script
cd /home/ec2-user/Optimization
./scripts/setup-from-github-secrets.sh

# Or manually check .env
cat .env
```

---

## 🔄 Common Commands

```bash
# View live logs
sudo journalctl -u streamlit-optimization.service -f

# Restart service
sudo systemctl restart streamlit-optimization.service

# Check service status
sudo systemctl status streamlit-optimization.service

# Check if app is responding
curl http://localhost:8501

# Check Nginx status
sudo systemctl status nginx

# Restart Nginx
sudo systemctl restart nginx
```

---

## ✅ Verification Checklist

After updating, verify:

- [ ] Code pulled successfully (`git log -1`)
- [ ] Service is running (`sudo systemctl status`)
- [ ] Port 8501 is listening (`curl http://localhost:8501`)
- [ ] Nginx is running (`sudo systemctl status nginx`)
- [ ] Can access from browser (clear cache first)
- [ ] No errors in logs (`sudo journalctl -u streamlit-optimization.service -n 20`)

---

## 🆘 Still Not Working?

If nothing works:

1. **Check the deployment status script:**
   ```bash
   ./scripts/check-deployment-status.sh
   ```

2. **View full logs:**
   ```bash
   sudo journalctl -u streamlit-optimization.service -n 100
   ```

3. **Re-run full deployment:**
   ```bash
   ./scripts/deploy-to-ec2.sh
   ```

4. **Check EC2 Security Group:**
   - Ensure port 80 is open
   - Ensure port 22 (SSH) is open

---

**Remember:** Always clear your browser cache or use incognito mode to see changes!

