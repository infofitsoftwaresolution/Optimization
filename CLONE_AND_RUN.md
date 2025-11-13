# 🚀 Clone and Run Guide

**The simplest guide to get the project running after cloning.**

## Step 1: Clone the Repository

```bash
git clone https://github.com/infofitsoftwaresolution/Optimization.git
cd Optimization
```

## Step 2: Run Automated Setup

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
- ✅ Create all necessary directories
- ✅ Create .env file from .env.example
- ✅ Create virtual environment
- ✅ Install all dependencies
- ✅ Verify installation

## Step 3: Configure Credentials

Edit the `.env` file and add your AWS credentials:

```env
AWS_ACCESS_KEY_ID=your_actual_access_key_here
AWS_SECRET_ACCESS_KEY=your_actual_secret_key_here
AWS_REGION=us-east-2
OPENAI_API_KEY=your_openai_key_here  # Optional
```

## Step 4: Start the Dashboard

**Windows:**
```bash
start_dashboard.bat
```

**Linux/Mac:**
```bash
chmod +x start_dashboard.sh
./start_dashboard.sh
```

## Step 5: Open Your Browser

The dashboard will automatically open at: **http://localhost:8501**

If it doesn't open automatically, manually navigate to that URL.

---

## ✅ Verify Installation

After setup, run this to verify everything is working:

```bash
python verify_setup.py
```

This will check:
- ✅ Python version
- ✅ Required directories
- ✅ Required files
- ✅ Environment configuration
- ✅ Virtual environment
- ✅ Installed dependencies

---

## 🐛 Troubleshooting

### Setup script fails

**Try manual setup:**
1. Create virtual environment: `python -m venv .venv`
2. Activate it: `.venv\Scripts\Activate.ps1` (Windows) or `source .venv/bin/activate` (Linux/Mac)
3. Install dependencies: `pip install -r requirements.txt`
4. Copy .env: `Copy-Item .env.example .env` (Windows) or `cp .env.example .env` (Linux/Mac)

### Dashboard won't start

**Check:**
1. Virtual environment is activated
2. Dependencies are installed: `pip list | grep streamlit`
3. Port 8501 is not in use: Try `streamlit run src/dashboard.py --server.port 8502`

### "NoCredentialsError"

**Solution:**
1. Make sure `.env` file exists
2. Check that AWS credentials are correct
3. Verify credentials have Bedrock access

---

## 📚 Need More Help?

- **Detailed installation:** See [INSTALL.md](INSTALL.md)
- **Quick start:** See [QUICK_START.md](QUICK_START.md)
- **Full documentation:** See [README.md](README.md)

---

**That's it! You're ready to use the dashboard! 🎉**

