# 📦 Installation Guide

Complete installation guide for setting up the AI Cost Optimizer project after cloning.

## 🚀 Quick Installation (Recommended)

### Option 1: Automated Setup (Easiest)

**Windows:**
```powershell
python setup.py
```

**Linux/Mac:**
```bash
python3 setup.py
```

This will automatically:
- ✅ Check Python version
- ✅ Create necessary directories
- ✅ Set up .env file from .env.example
- ✅ Create virtual environment
- ✅ Install all dependencies
- ✅ Verify installation

### Option 2: Manual Setup

Follow the steps below if you prefer manual setup or if automated setup fails.

---

## 📋 Prerequisites

Before starting, ensure you have:

- **Python 3.8 or higher** installed
  - Check: `python --version` or `python3 --version`
  - Download: https://www.python.org/downloads/
- **Git** installed (for cloning)
- **AWS Account** with Bedrock access
- **AWS Credentials** (Access Key ID and Secret Access Key)
- **(Optional) OpenAI API Key** for master model comparison

---

## 🔧 Step-by-Step Manual Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/infofitsoftwaresolution/Optimization.git
cd Optimization
```

### Step 2: Run Setup Script

```bash
# Windows
python setup.py

# Linux/Mac
python3 setup.py
```

### Step 3: Create Virtual Environment (if not done automatically)

**Windows:**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**Linux/Mac:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 5: Configure Environment Variables

1. Copy the example environment file:
   ```bash
   # Windows PowerShell
   Copy-Item .env.example .env
   
   # Windows CMD
   copy .env.example .env
   
   # Linux/Mac
   cp .env.example .env
   ```

2. Edit `.env` file and add your credentials:
   ```env
   AWS_ACCESS_KEY_ID=your_actual_access_key_here
   AWS_SECRET_ACCESS_KEY=your_actual_secret_key_here
   AWS_REGION=us-east-2
   OPENAI_API_KEY=your_openai_key_here  # Optional
   ```

### Step 6: Verify Installation

```bash
python -c "import streamlit, pandas, boto3, numpy, plotly, openai; print('✅ All packages installed!')"
```

### Step 7: Start the Dashboard

**Option A: Using Startup Scripts (Easiest)**

**Windows:**
```bash
start_dashboard.bat
```

**Linux/Mac:**
```bash
chmod +x start_dashboard.sh
./start_dashboard.sh
```

**Option B: Manual Start**

Make sure virtual environment is activated, then:
```bash
streamlit run src/dashboard.py
```

The dashboard will open at: **http://localhost:8501**

---

## ✅ Verification Checklist

After installation, verify:

- [ ] Python 3.8+ is installed
- [ ] Virtual environment is created (`.venv` folder exists)
- [ ] Dependencies are installed (check with `pip list`)
- [ ] `.env` file exists and contains your AWS credentials
- [ ] `configs/models.yaml` exists
- [ ] Dashboard starts without errors
- [ ] Dashboard opens in browser at http://localhost:8501

---

## 🐛 Troubleshooting

### "Python not found" or "python: command not found"

**Solution:**
- Make sure Python is installed and added to PATH
- Try `python3` instead of `python` on Linux/Mac
- Reinstall Python and check "Add Python to PATH" during installation

### "ModuleNotFoundError" when running dashboard

**Solution:**
1. Make sure virtual environment is activated:
   ```bash
   # Windows
   .venv\Scripts\Activate.ps1
   
   # Linux/Mac
   source .venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### "NoCredentialsError" or AWS authentication errors

**Solution:**
1. Check that `.env` file exists in project root
2. Verify AWS credentials in `.env` file are correct
3. Make sure credentials have Bedrock access permissions
4. Try using AWS CLI: `aws configure`

### "Port 8501 already in use"

**Solution:**
- Use a different port:
  ```bash
  streamlit run src/dashboard.py --server.port 8502
  ```
- Or stop the process using port 8501:
  ```bash
  # Windows
  netstat -ano | findstr :8501
  taskkill /PID <PID> /F
  ```

### Virtual environment activation fails (Windows PowerShell)

**Solution:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Permission denied errors (Linux/Mac)

**Solution:**
```bash
chmod +x start_dashboard.sh
chmod +x setup.py
```

---

## 📚 Additional Resources

- **[QUICK_START.md](QUICK_START.md)** - 5-minute quick start guide
- **[README.md](README.md)** - Full project documentation
- **[MANUAL_RUN_GUIDE.md](MANUAL_RUN_GUIDE.md)** - Detailed manual setup guide
- **[SETUP_CHECKLIST.md](SETUP_CHECKLIST.md)** - Step-by-step verification checklist

---

## 🆘 Still Having Issues?

1. Check the [Troubleshooting](#-troubleshooting) section above
2. Review error messages carefully
3. Ensure all prerequisites are met
4. Try the manual setup steps
5. Check GitHub Issues for similar problems

---

## ✅ Success!

Once you see the dashboard running at http://localhost:8501, you're all set! 🎉

You can now:
- Upload CloudWatch logs
- Run model evaluations
- Compare model performance
- Use master model comparison (if OpenAI API key is configured)

