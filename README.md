# Model Evaluation Framework for AWS Bedrock LLMs

A comprehensive framework to compare multiple AWS Bedrock LLMs using production-like prompts. Measure latency, token usage, JSON validity, and cost, then visualize results in an interactive Streamlit dashboard.

---

## 🚀 Quick Start (After Cloning)

**The fastest way to get started:**

```bash
# 1. Run automated setup
python setup.py

# 2. Configure your .env file with AWS credentials
# Edit .env and add your AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY

# 3. Start the dashboard
# Windows:
start_dashboard.bat

# Linux/Mac:
chmod +x start_dashboard.sh
./start_dashboard.sh
```

**That's it!** The dashboard will open at http://localhost:8501

---

## 📚 Documentation

Choose the guide that fits your needs:

- **[INSTALL.md](INSTALL.md)** - Complete installation guide (start here if you just cloned)
- **[QUICK_START.md](QUICK_START.md)** - 5-minute quick start (for experienced developers)
- **[MANUAL_RUN_GUIDE.md](MANUAL_RUN_GUIDE.md)** - Detailed step-by-step instructions
- **[SETUP_CHECKLIST.md](SETUP_CHECKLIST.md)** - Verification checklist

---

## ✨ Features

- **Multi-model evaluation** - Test multiple Bedrock models with the same prompts
- **Comprehensive metrics** - Latency, token usage, JSON validity, and cost tracking
- **Interactive dashboard** - Visualize results with charts and comparisons
- **CloudWatch integration** - Upload and parse CloudWatch logs, extract prompts
- **Master model comparison** - Compare outputs against ChatGPT/OpenAI models
- **Similarity scoring** - Calculate similarity percentages between model outputs
- **Config-driven** - Manage models and pricing via YAML configuration
- **Export capabilities** - Download results as CSV for further analysis

---

## 📋 Prerequisites

- **Python 3.8+** - [Download Python](https://www.python.org/downloads/)
- **AWS Account** with Bedrock access
- **AWS Credentials** (Access Key ID and Secret Access Key)
- **(Optional) OpenAI API Key** - For master model comparison feature

---

## 🔧 Installation

### Automated Setup (Recommended)

```bash
python setup.py
```

This will automatically:
- ✅ Check Python version
- ✅ Create necessary directories
- ✅ Set up .env file
- ✅ Create virtual environment
- ✅ Install dependencies
- ✅ Verify installation

### Manual Setup

See [INSTALL.md](INSTALL.md) for detailed manual installation instructions.

---

## ⚙️ Configuration

### AWS Credentials

**Option 1: Using .env file (Recommended)**

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
   OPENAI_API_KEY=your_openai_key_here  # Optional
   ```

**Option 2: Using AWS CLI**

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

## 🎯 Usage

### Starting the Dashboard

**Using startup scripts (easiest):**

**Windows:**
```bash
start_dashboard.bat
```

**Linux/Mac:**
```bash
chmod +x start_dashboard.sh
./start_dashboard.sh
```

**Manual start:**
```bash
# Activate virtual environment first
# Windows: .venv\Scripts\Activate.ps1
# Linux/Mac: source .venv/bin/activate

streamlit run src/dashboard.py
```

The dashboard will open at `http://localhost:8501`

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

## 📊 Features Overview

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

## 🐛 Troubleshooting

### Common Issues

**"ModuleNotFoundError"**
```bash
# Make sure virtual environment is activated
pip install -r requirements.txt
```

**"NoCredentialsError"**
- Verify AWS credentials in `.env` file
- Check that credentials have Bedrock permissions

**"Port 8501 already in use"**
```bash
streamlit run src/dashboard.py --server.port 8502
```

**Dashboard shows "No data found"**
- This is normal for a fresh installation
- Run an evaluation or upload CloudWatch logs to get started

For more troubleshooting, see [INSTALL.md](INSTALL.md#-troubleshooting)

---

## 🔐 Security Notes

- **Never commit** `.env` file to version control
- Use AWS IAM roles with minimal required permissions
- Review AWS CloudTrail logs regularly
- Keep dependencies updated for security patches

---

## 🚀 CI/CD Deployment

This project includes automated CI/CD deployment to EC2 using GitHub Actions.

**Repository:** https://github.com/infofitsoftwaresolution/Optimization

For deployment details, see:
- [DEPLOYMENT.md](DEPLOYMENT.md) - Deployment guide
- [CI_CD_STATUS.md](CI_CD_STATUS.md) - CI/CD status and monitoring
- [AUTOMATIC_DEPLOYMENT.md](AUTOMATIC_DEPLOYMENT.md) - Automatic deployment guide

---

## 📚 Additional Resources

- [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [boto3 Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

## 📄 License

[Add your license here]

---

## 💡 Tips

- Start with a small test evaluation before running large batches
- Use different run IDs to compare different configurations
- Export results regularly for tracking over time
- Monitor AWS costs in CloudWatch

---

## 🆘 Need Help?

- **Installation issues?** See [INSTALL.md](INSTALL.md)
- **Quick start?** See [QUICK_START.md](QUICK_START.md)
- **Detailed guide?** See [MANUAL_RUN_GUIDE.md](MANUAL_RUN_GUIDE.md)
- **Verification?** See [SETUP_CHECKLIST.md](SETUP_CHECKLIST.md)

---

## ✅ Latest Deployment

**Last updated:** 2025-01-13  
**CI/CD Status:** ✅ Active  
**Deployment Target:** EC2 (3.111.36.145:8501)

---

**Happy Evaluating! 🎉**
