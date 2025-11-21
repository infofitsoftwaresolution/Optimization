# Model Evaluation Framework for AWS Bedrock LLMs

A comprehensive framework to compare multiple AWS Bedrock LLMs using production-like prompts. Measure latency, token usage, JSON validity, and cost, then visualize results in an interactive Streamlit dashboard.

---

##  Quick Start (After Cloning)

**New to this project? Follow these simple steps:**

### Prerequisites Checklist

Before starting, make sure you have:
-  Python 3.8 or higher installed ([Download here](https://www.python.org/downloads/))
-  AWS Account with Bedrock access
-  AWS Access Key ID and Secret Access Key
-  (Optional) OpenAI API Key for master model comparison

### Step 1: Run Automated Setup

```bash
python setup.py
```

This will:
-  Check Python version (requires 3.8+)
-  Create necessary directories
-  Create virtual environment (`.venv`)
-  Set up `.env` file template
-  Install all dependencies

**Note:** The setup script will automatically install all dependencies. This may take a few minutes.

### Step 2: Configure AWS Credentials

Edit the `.env` file in the project root and add your credentials:

```env
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_REGION=us-east-2
OPENAI_API_KEY=your_openai_key_here  # Optional, for master model comparison
```

**Important:** Replace the placeholder values with your actual credentials!

### Step 3: Start the Dashboard

**Windows:**
```bash
start_dashboard.bat
```

**Linux/Mac:**
```bash
chmod +x start_dashboard.sh
./start_dashboard.sh
```

**Manual Start (if scripts don't work):**
```bash
# Windows PowerShell:
.venv\Scripts\Activate.ps1
streamlit run src/dashboard.py

# Windows CMD:
.venv\Scripts\activate.bat
streamlit run src/dashboard.py

# Linux/Mac:
source .venv/bin/activate
streamlit run src/dashboard.py
```

### Step 4: Access the Dashboard

Once the server starts, you'll see:
```
You can now view your Streamlit app in your browser.
Local URL: http://localhost:8501
```

**Open your browser and go to:** http://localhost:8501

**Note:** The startup scripts automatically skip the Streamlit email prompt. If you're running manually and see the email prompt, just press Enter to skip.

### Step 5: Verify Everything Works

Once the dashboard loads, you should see:
-  The dashboard interface with sidebar and main content area
-  No error messages in the browser
-  The terminal shows the server is running

If you see any errors, check the [Troubleshooting](#-troubleshooting) section below.

**That's it!** The dashboard should now be running. 

---

---

##  Features

- **Multi-model evaluation** - Test multiple Bedrock models with the same prompts
- **Comprehensive metrics** - Latency, token usage, JSON validity, and cost tracking
- **Interactive dashboard** - Visualize results with charts and comparisons
- **CloudWatch integration** - Upload and parse CloudWatch logs, extract prompts
- **Master model comparison** - Compare outputs against ChatGPT/OpenAI models
- **Similarity scoring** - Calculate similarity percentages between model outputs
- **Config-driven** - Manage models and pricing via YAML configuration
- **Export capabilities** - Download results as CSV for further analysis

---

##  Prerequisites

- **Python 3.8+** - [Download Python](https://www.python.org/downloads/)
- **AWS Account** with Bedrock access
- **AWS Credentials** (Access Key ID and Secret Access Key)
- **(Optional) OpenAI API Key** - For master model comparison feature

---

##  Installation

### Automated Setup (Recommended)

```bash
python setup.py
```

This will automatically:
-  Check Python version
-  Create necessary directories
-  Set up .env file
-  Create virtual environment
-  Install dependencies
-  Verify installation

### Manual Setup

If you prefer to set up manually:

1. **Create virtual environment:**
   ```bash
   python -m venv .venv
   ```

2. **Activate virtual environment:**
   ```bash
   # Windows
   .venv\Scripts\activate
   # Linux/Mac
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create .env file:**
   ```bash
   # Windows
   Copy-Item .env.example .env
   # Linux/Mac
   cp .env.example .env
   ```

5. **Edit .env file** and add your AWS credentials.

---

## ⚙️ Configuration

### AWS Credentials

**Option 1: Using GitHub Secrets (Recommended for Team/EC2 Deployment)**

If you're deploying on EC2 or working with a team, use GitHub Secrets to securely store credentials:

1. **Add secrets to GitHub:**
   - Go to your repository → Settings → Secrets and variables → Actions
   - Add these secrets:
     - `AWS_ACCESS_KEY_ID`
     - `AWS_SECRET_ACCESS_KEY`
     - `AWS_REGION`
     - `DB_HOST`
     - `DB_PORT`
     - `DB_NAME`
     - `DB_USER`
     - `DB_PASSWORD`
     - `OPENAI_API_KEY` (optional)

2. **On EC2, run the setup script:**
   ```bash
   # Linux/Mac
   chmod +x scripts/setup-from-github-secrets.sh
   ./scripts/setup-from-github-secrets.sh
   
   # Windows PowerShell
   .\scripts\setup-from-github-secrets.ps1
   ```

   This script will:
   - Install GitHub CLI if needed
   - Authenticate with GitHub
   - Download all secrets
   - Create a `.env` file automatically

📖 **See [GITHUB_SECRETS_SETUP.md](GITHUB_SECRETS_SETUP.md) for detailed step-by-step instructions.**

**Option 2: Using .env file (Local Development)**

The setup script automatically creates a `.env` file from `.env.example`. If you need to create it manually:

1. Copy the example file:
   ```bash
   # Windows
   Copy-Item .env.example .env
   
   # Linux/Mac
   cp .env.example .env
   ```

2. Edit `.env` and add your credentials:
   ```env
   AWS_ACCESS_KEY_ID=your_access_key_here
   AWS_SECRET_ACCESS_KEY=your_secret_key_here
   AWS_REGION=us-east-2
   DB_HOST=your_db_host_here
   DB_PORT=5432
   DB_NAME=bellatrix_db
   DB_USER=postgres
   DB_PASSWORD=your_db_password_here
   OPENAI_API_KEY=your_openai_key_here  # Optional
   ```

**Option 3: Using AWS CLI**

```bash
aws configure
```

### Model Configuration

Edit `configs/models.yaml` to configure your models:

```yaml
region_name: us-east-2

models:
  - name: Claude 3.7 Sonnet
    provider: anthropic
    bedrock_model_id: us.anthropic.claude-3-7-sonnet-20250219-v1:0
    tokenizer: anthropic
    pricing:
      input_per_1k_tokens_usd: 0.008
      output_per_1k_tokens_usd: 0.024
    generation_params:
      max_tokens: 1500
      temperature: 0.7
      top_p: 0.95
```

**Note:** Ensure the models are enabled in your AWS Bedrock account before running evaluations.

---

##  Usage

### Starting the Dashboard

**Using startup scripts (recommended):**

**Windows:**
```bash
start_dashboard.bat
```

**Linux/Mac:**
```bash
chmod +x start_dashboard.sh
./start_dashboard.sh
```

**Manual start (if scripts don't work):**

**Windows PowerShell:**
```powershell
.venv\Scripts\Activate.ps1
streamlit run src/dashboard.py
```

**Windows Command Prompt:**
```cmd
.venv\Scripts\activate.bat
streamlit run src/dashboard.py
```

**Linux/Mac:**
```bash
source .venv/bin/activate
streamlit run src/dashboard.py
```

**What to expect:**
- The server will start and display: `Local URL: http://localhost:8501`
- The startup scripts automatically skip the Streamlit email prompt (no action needed)
- The dashboard will automatically open in your browser (or visit http://localhost:8501 manually)
- Keep the terminal window open while using the dashboard
- Press `Ctrl+C` in the terminal to stop the server

**Troubleshooting startup:**
- If you see "Virtual environment not found", run `python setup.py` first
- If you see "ModuleNotFoundError", the startup script will try to install dependencies automatically
- If port 8501 is in use, see the [Troubleshooting](#-troubleshooting) section for solutions

### Running Evaluations

1. **Enter a prompt** in the sidebar or upload a file
2. **Select models** to evaluate
3. **Enable master model comparison** (optional) to compare against ChatGPT
4. **Click "Run Evaluation"**
5. **View results** with interactive charts and metrics

### CloudWatch Integration

1. **Upload CloudWatch log file** (.jsonl format)
2. **View parsed metrics** and extracted prompts
3. **Select prompts** from logs to use for evaluation
4. **Run evaluations** with selected prompts

---

##  Features Overview

### Dashboard Features

- **Summary Cards** - Total evaluations, success rate, cost, models compared
- **Model Comparison Table** - Aggregated metrics per model
- **Best Performer Highlights** - Best latency, cost, and JSON validity
- **Interactive Visualizations**:
  - Latency distribution (box plots)
  - Token usage (bar charts)
  - Cost analysis
  - JSON validity percentages
- **Master Model Comparison** - Similarity scores against reference model
- **Export Options** - Download results as CSV

### Similarity Measurement

The system uses a **combined similarity algorithm**:
- **Cosine Similarity** (50% weight) - Word frequency vectors
- **Jaccard Similarity** (30% weight) - Word set overlap
- **Levenshtein Similarity** (20% weight) - Character-level edit distance

Final score = (Cosine × 0.5) + (Jaccard × 0.3) + (Levenshtein × 0.2)

---

## 🗂️ Project Structure

```
Optimization/
├── src/                    # Source code
│   ├── dashboard.py        # Streamlit dashboard
│   ├── evaluator.py        # Model evaluation logic
│   ├── cloudwatch_parser.py # CloudWatch log parser
│   ├── master_model_evaluator.py # OpenAI/ChatGPT integration
│   ├── similarity_calculator.py # Similarity scoring
│   ├── model_registry.py   # Model configuration management
│   └── utils/              # Utility modules
├── configs/                # Configuration files
│   ├── models.yaml         # Model definitions and pricing
│   └── settings.yaml       # Application settings
├── data/                   # Data directory
│   ├── runs/               # Evaluation results (generated)
│   └── cache/              # Cache files
├── scripts/                # Utility scripts
│   └── run_evaluation.py   # Run model evaluations
├── setup.py                # Automated setup script
├── start_dashboard.bat     # Windows startup script
├── start_dashboard.sh      # Linux/Mac startup script
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

---

##  Troubleshooting

### Common Issues

**"ModuleNotFoundError" or "No module named 'streamlit'"**
```bash
# Make sure virtual environment is activated first
# Windows:
.venv\Scripts\Activate.ps1
# Linux/Mac:
source .venv/bin/activate

# Then install dependencies
pip install -r requirements.txt
```

**"Virtual environment not found"**
```bash
# Create virtual environment
python -m venv .venv

# Activate it (Windows):
.venv\Scripts\Activate.ps1
# Activate it (Linux/Mac):
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**"NoCredentialsError" or AWS authentication errors**
- Verify AWS credentials in `.env` file exist and are correct
- Check that credentials have Bedrock permissions
- Ensure `.env` file is in the project root directory
- Try using AWS CLI: `aws configure` (alternative method)

**"Port 8501 already in use"**
```bash
# Option 1: Use a different port
streamlit run src/dashboard.py --server.port 8502

# Option 2: Find and stop the process using port 8501
# Windows:
netstat -ano | findstr :8501
taskkill /PID <PID_NUMBER> /F

# Linux/Mac:
lsof -ti:8501 | xargs kill -9
```

**"localhost refused to connect" or "ERR_CONNECTION_REFUSED"**
- Make sure the Streamlit server is actually running (check terminal output)
- Wait a few seconds after starting - the server needs time to initialize
- Try accessing `http://127.0.0.1:8501` instead of `http://localhost:8501`
- Check if Windows Firewall is blocking the connection
- Ensure you're using the correct port (check terminal output for the actual URL)

**Streamlit email prompt blocking startup**
- This is normal on first run
- Simply press Enter to skip
- Or set environment variable: `$env:STREAMLIT_BROWSER_GATHER_USAGE_STATS="false"` (Windows PowerShell)

**"Permission denied" when running start_dashboard.sh (Linux/Mac)**
```bash
chmod +x start_dashboard.sh
./start_dashboard.sh
```

**Dashboard shows "No data found"**
- This is normal for a fresh installation
- Run an evaluation or upload CloudWatch logs to get started
- The dashboard needs evaluation data to display results

**Python version errors**
- Ensure Python 3.8 or higher is installed
- Check version: `python --version` or `python3 --version`
- Download from: https://www.python.org/downloads/

**Windows PowerShell execution policy errors**
```powershell
# Run PowerShell as Administrator, then:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

If you continue to experience issues, please check:
- Python version is 3.8 or higher
- Virtual environment is activated
- All dependencies are installed
- AWS credentials are correctly configured in `.env` file

---

##  Security Notes

- **Never commit** `.env` file to version control
- Use AWS IAM roles with minimal required permissions
- Review AWS CloudTrail logs regularly
- Keep dependencies updated for security patches

---

##  CI/CD Deployment

This project includes automated CI/CD deployment to EC2 using GitHub Actions.

**Repository:** https://github.com/infofitsoftwaresolution/Optimization

For deployment details, see:
- [DEPLOYMENT.md](DEPLOYMENT.md) - Deployment guide
- [CI_CD_STATUS.md](CI_CD_STATUS.md) - CI/CD status and monitoring
- [AUTOMATIC_DEPLOYMENT.md](AUTOMATIC_DEPLOYMENT.md) - Automatic deployment guide

---

##  Additional Resources

- [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [boto3 Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)

---

##  Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

##  License

[Add your license here]

---

##  Tips

- Start with a small test evaluation before running large batches
- Use different run IDs to compare different configurations
- Export results regularly for tracking over time
- Monitor AWS costs in CloudWatch

---

##  Need Help?

If you encounter any issues:

1. **Check the Troubleshooting section** above for common problems
2. **Verify your setup:**
   - Python 3.8+ is installed
   - Virtual environment is created and activated
   - Dependencies are installed (`pip list` should show streamlit, boto3, etc.)
   - `.env` file exists and has correct AWS credentials
3. **Check the terminal output** for specific error messages
4. **Ensure AWS Bedrock models are enabled** in your AWS account

---

##  Latest Deployment

**Last updated:** 2025-01-13  
**CI/CD Status:**  Active  
**Deployment Target:** EC2 (3.111.36.145:8501)

---

**Happy Evaluating! **
