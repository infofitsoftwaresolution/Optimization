# 🚀 Quick Setup Instructions for New Users

This guide ensures anyone who clones this project can get it running quickly with the same configuration.

## ⚡ Quick Start (5 minutes)

### 1. Clone the Repository
```bash
git clone <repository-url>
cd Optimization
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure AWS Credentials

**Option A: Using .env file (Recommended)**

1. Copy the example file:
   ```bash
   # Windows PowerShell
   Copy-Item .env.example .env
   
   # Linux/Mac
   cp .env.example .env
   ```

2. Edit `.env` and add your credentials:
   ```env
   AWS_ACCESS_KEY_ID=your_access_key_here
   AWS_SECRET_ACCESS_KEY=your_secret_key_here
   AWS_REGION=us-east-2
   ```

**Option B: Using AWS Profile**

Set in `config.py` or as environment variable:
```python
AWS_PROFILE = "your-profile-name"
```

**Option C: Using AWS CLI**

```bash
aws configure
```

### 4. Enable Anthropic Models (Required for Claude)

**⚠️ IMPORTANT:** Claude models need manual approval in AWS Bedrock.

1. Go to: https://console.aws.amazon.com/bedrock/home?region=us-east-2#/modelaccess
2. Find "Anthropic" → Click "Request model access"
3. Fill out the form and submit
4. Wait 5-15 minutes for approval

See `FIX_ANTHROPIC_ACCESS.md` for detailed steps.

### 5. Run the Dashboard

```bash
streamlit run src/dashboard.py
```

The dashboard will open at `http://localhost:8501`

### 6. Run Your First Evaluation

**Via Dashboard:**
- Enter a prompt in the sidebar
- Select both models (Claude 3.7 Sonnet and Llama 3.2 11B Instruct)
- Click "🚀 Run Evaluation"

**Via Command Line:**
```bash
python evaluate.py --models claude-sonnet llama-3-2-11b --max-prompts 3
```

## 📋 Configured Models

The project is pre-configured with **only these two models**:

1. **Claude 3.7 Sonnet**
   - Model ID: `us.anthropic.claude-3-7-sonnet-20250219-v1:0`
   - Provider: Anthropic
   - Requires: Anthropic model access approval

2. **Llama 3.2 11B Instruct**
   - Model ID: `us.meta.llama3-2-11b-instruct-v1:0`
   - Provider: Meta
   - No approval required

## 🎯 What You'll See

After running evaluations, the dashboard will show:

- **Executive Summary**: Total evaluations, success rate, cost, models compared
- **Performance Leaders**: Fastest, most cost-effective, best quality
- **Interactive Analytics**: Response time distribution, requests per model, cost analysis
- **Detailed Results**: Full metrics table with all evaluation data

The dashboard will **only show these two configured models** - all other models are filtered out.

## 🐛 Common Issues

### "NoCredentialsError"
- Make sure you've set AWS credentials in `.env` or AWS CLI
- Verify credentials are correct

### "Model use case details have not been submitted"
- Enable Anthropic models in AWS Bedrock (Step 4 above)
- See `FIX_ANTHROPIC_ACCESS.md` for help

### Dashboard shows "No data found"
- Run an evaluation first using the sidebar or command line
- Check that models are enabled in your AWS account

### Dashboard shows wrong number of models
- The dashboard is configured to show only 2 models
- If you see more, check `configs/models.yaml` and ensure only the two models are listed

## 📁 Important Files

- `config.py` - Main configuration (uses environment variables)
- `configs/models.yaml` - Model definitions for dashboard
- `.env` - Your AWS credentials (create from `.env.example`)
- `src/dashboard.py` - Streamlit dashboard application
- `data/runs/` - Evaluation results (auto-generated)

## 🔒 Security Notes

- Never commit `.env` file to git (it's in `.gitignore`)
- Never commit `config.py` with real credentials
- Use environment variables for credentials when possible

---

**Need Help?** Check `MANUAL_GUIDE.md` for detailed instructions or `FIX_ANTHROPIC_ACCESS.md` for Anthropic access issues.

