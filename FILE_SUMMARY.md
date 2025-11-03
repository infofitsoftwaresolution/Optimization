# Complete File Summary - AI Cost Optimizer

This document provides a detailed explanation of every file in the project, what it does, and why it's needed for AWS EC2 deployment.

---

## 📁 Root Directory Files

### 1. `requirements.txt`
**What it does:**
- Lists all Python package dependencies needed to run the application
- Specifies minimum versions for each package

**Why needed:**
- **Critical for deployment**: EC2 server needs to install all dependencies
- Used by `pip install -r requirements.txt` to set up the environment
- Ensures consistent package versions across environments

**Key dependencies:**
- `boto3`: AWS SDK for interacting with Bedrock
- `streamlit`: Web framework for the dashboard
- `pandas`, `numpy`: Data processing and analysis
- `plotly`: Interactive visualizations
- `tiktoken`: Accurate token counting
- `PyYAML`: Reading model configuration files

---

### 2. `README.md`
**What it does:**
- Main project documentation
- Explains what the application does
- Provides usage instructions and examples

**Why needed:**
- **Essential for understanding**: Explains project purpose and features
- Helps new users/developers understand the system
- Contains setup instructions and usage examples

---

### 3. `DEPLOYMENT.md`
**What it does:**
- Step-by-step guide for deploying to AWS EC2
- Instructions for setting up the server
- Configuration and security recommendations

**Why needed:**
- **Critical for deployment**: Provides deployment instructions
- Helps configure EC2 instance correctly
- Explains systemd service setup for production

---

### 4. `start_dashboard.sh`
**What it does:**
- Linux/Unix startup script for the Streamlit dashboard
- Checks Python installation
- Installs dependencies
- Clears cache and starts the server

**Why needed:**
- **Essential for EC2**: Automates server startup on Linux
- Handles port conflicts
- Provides easy way to start the dashboard: `./start_dashboard.sh`

---

### 5. `.gitignore`
**What it does:**
- Tells Git which files to ignore
- Excludes cache files, logs, and generated data

**Why needed:**
- **Good practice**: Prevents committing unnecessary files
- Keeps repository clean
- Excludes `__pycache__`, generated CSVs, logs, etc.

---

## 📁 `configs/` Directory

### 6. `configs/models.yaml`
**What it does:**
- Defines all LLM models to test (Claude, Llama, etc.)
- Contains model configurations:
  - AWS Bedrock model IDs
  - Pricing per 1k tokens (input/output)
  - Generation parameters (temperature, max_tokens, top_p)
  - Tokenizer types

**Why needed:**
- **Core configuration**: Without this, no models can be evaluated
- Centralizes all model settings
- Easy to add/remove models or update pricing
- Used by `ModelRegistry` to load model configurations

**Example content:**
```yaml
models:
  - name: Claude 3.5 Sonnet
    provider: anthropic
    bedrock_model_id: us.anthropic.claude-3-5-sonnet-20240620-v1:0
    pricing:
      input_per_1k_tokens_usd: 0.003
      output_per_1k_tokens_usd: 0.015
```

---

### 7. `configs/settings.yaml`
**What it does:**
- General application settings (if used)
- May contain default paths, regions, or other configuration

**Why needed:**
- **Optional but useful**: Centralizes application settings
- Allows configuration changes without code changes

---

## 📁 `src/` Directory (Core Application Code)

### 8. `src/__init__.py`
**What it does:**
- Makes `src/` a Python package
- Contains package metadata/description

**Why needed:**
- **Required by Python**: Allows importing modules from `src/`
- Enables `from src.evaluator import BedrockEvaluator` syntax
- Standard Python package structure

---

### 9. `src/dashboard.py` ⭐ **MAIN FILE**
**What it does:**
- **Main Streamlit web application**
- Creates the entire dashboard UI:
  - Sidebar with prompt input, file upload, model selection
  - Tabs for Overview & Analytics, Historical Results
  - Interactive charts and visualizations
  - Real-time evaluation execution
  - Results display and export

**Why needed:**
- **THE CORE APPLICATION**: This is what users interact with
- Entry point: Run with `streamlit run src/dashboard.py`
- Orchestrates all other components
- Handles user interface, state management, and data visualization

**Key features:**
- Premium UI with charts and metrics
- Real-time evaluation from sidebar
- Executive summary, performance leaders, interactive analytics
- Historical data exploration and export

---

### 10. `src/evaluator.py` ⭐ **CORE LOGIC**
**What it does:**
- **Executes prompts against AWS Bedrock models**
- Handles API calls to Bedrock (Converse API for Claude, InvokeModel for others)
- Collects performance metrics:
  - Token counts (input/output) - uses actual API counts when available
  - Latency (response time)
  - Cost calculation (based on actual token counts and pricing)
  - JSON validation
  - Error handling

**Why needed:**
- **Critical component**: Does the actual LLM evaluation work
- Interfaces with AWS Bedrock APIs
- Uses CountTokens API for accurate token counting
- Calculates costs based on actual API token counts
- Returns metrics for dashboard display

**Key methods:**
- `evaluate_prompt()`: Main method to test a prompt against a model
- `_invoke_converse()`: Calls Anthropic Claude via Converse API
- `_invoke_model_direct()`: Calls other models via InvokeModel API
- `_get_actual_input_tokens()`: Uses CountTokens API for accurate counts

---

### 11. `src/model_registry.py`
**What it does:**
- Loads and manages model configurations from `configs/models.yaml`
- Provides methods to:
  - List all models
  - Get model by name
  - Get model pricing
  - Get generation parameters

**Why needed:**
- **Configuration management**: Centralizes model configuration access
- Used by dashboard and evaluator to access model settings
- Makes it easy to add/change models without code changes
- Provides pricing data for cost calculations

---

### 12. `src/metrics_logger.py`
**What it does:**
- **Saves evaluation results to CSV files**
- Writes metrics to `data/runs/raw_metrics.csv`
- Appends new results to existing data
- Ensures consistent column structure

**Why needed:**
- **Data persistence**: Saves evaluation results for later analysis
- Creates historical dataset for dashboard charts
- Allows exporting and analyzing past evaluations
- Used by dashboard to load historical data

**Saves:**
- Timestamp, run_id, model_name, prompt_id
- Input/output tokens, latency, cost
- JSON validity, status, errors

---

### 13. `src/report_generator.py`
**What it does:**
- **Generates aggregated summary reports**
- Aggregates raw metrics into model-level statistics:
  - Average latency (p50, p95, p99)
  - Average tokens and costs
  - Success rates and JSON validity percentages
- Saves to `data/runs/model_comparison.csv`

**Why needed:**
- **Analytics**: Creates summary statistics for dashboard charts
- Powers the "Executive Summary" and "Performance Leaders" sections
- Provides model comparison data
- Aggregates thousands of raw records into meaningful metrics

---

### 14. `src/tokenizers.py`
**What it does:**
- **Counts tokens in text** using appropriate tokenizers
- Supports different tokenizer types:
  - Anthropic (Claude): Uses tiktoken with `cl100k_base` encoding
  - Llama: Uses tiktoken with `gpt2` encoding
  - Generic: Heuristic estimation (chars/words)

**Why needed:**
- **Token counting**: Estimates input tokens when API doesn't provide them
- Fallback when CountTokens API unavailable
- Uses accurate tokenizers (tiktoken) for better estimates
- Critical for cost calculation when API tokens unavailable

**Note**: System prioritizes actual API token counts, but uses this for fallback/estimation.

---

### 15. `src/prompt_loader.py`
**What it does:**
- Loads prompts from CSV files
- Validates CSV has required columns
- Auto-generates prompt_id if missing

**Why needed:**
- **File processing**: Handles prompt CSV file loading
- Used by command-line script `run_evaluation.py`
- Ensures proper CSV format before processing
- Minimal but important for batch processing

---

## 📁 `src/utils/` Directory (Utility Modules)

### 16. `src/utils/bedrock_client.py`
**What it does:**
- **Creates AWS Bedrock client** using boto3
- Configures retry logic and timeouts
- Handles region configuration

**Why needed:**
- **AWS Integration**: Creates the client connection to Bedrock
- Centralizes client creation logic
- Configures retries for reliability
- Used by evaluator to make API calls

---

### 17. `src/utils/json_utils.py`
**What it does:**
- Validates JSON strings
- Safely parses JSON with error handling
- Used for validating LLM responses

**Why needed:**
- **Response validation**: Checks if LLM responses are valid JSON
- Safe error handling prevents crashes
- Used by dashboard to validate JSON responses
- Provides validation metrics (json_valid field)

---

### 18. `src/utils/timing.py`
**What it does:**
- Simple timing utility using context manager
- Measures elapsed time in milliseconds
- Used by evaluator to measure latency

**Why needed:**
- **Performance measurement**: Measures how long API calls take
- Provides latency metrics for dashboard
- Simple, reusable timing utility

---

## 📁 `scripts/` Directory (Utility Scripts)

### 19. `scripts/run_evaluation.py`
**What it does:**
- **Command-line script for batch evaluation**
- Runs evaluations from terminal (outside dashboard)
- Processes CSV files with prompts
- Supports filtering by models, limiting prompts, etc.

**Why needed:**
- **Batch processing**: Run evaluations programmatically
- Useful for automated testing or CI/CD
- Can process large CSV files of prompts
- Alternative to dashboard for command-line users

**Usage:**
```bash
python scripts/run_evaluation.py --models all --prompts data/prompts.csv
```

---

### 20. `scripts/extract_prompts_from_json.py`
**What it does:**
- Extracts prompts from JSON/JSONL files
- Useful for processing Bedrock CloudTrail logs
- Converts JSON data to CSV format for evaluation

**Why needed:**
- **Data processing utility**: Converts JSON logs to usable CSV format
- Helps extract prompts from various JSON formats
- Useful for analyzing existing API usage data

---

## 📁 `data/` Directory

### 21. `data/runs/raw_metrics.csv`
**What it does:**
- **Stores all evaluation results** (one row per evaluation)
- Contains detailed metrics: tokens, latency, cost, status
- Appended to by MetricsLogger after each evaluation

**Why needed:**
- **Data storage**: Historical record of all evaluations
- Used by dashboard to display historical data
- Can be exported for external analysis
- Powers all historical charts and analytics

**Note**: This file grows over time as evaluations are run.

---

### 22. `data/runs/model_comparison.csv`
**What it does:**
- **Aggregated summary statistics** per model
- Generated by ReportGenerator
- Contains averages, percentiles, totals

**Why needed:**
- **Analytics**: Powers dashboard summary sections
- Faster queries than raw_metrics.csv
- Used for "Executive Summary" and "Performance Leaders"

**Note**: Regenerated when new evaluations are run.

---

### 23. `data/runs/.gitkeep`
**What it does:**
- Empty file to ensure `data/runs/` directory exists in Git
- Preserves directory structure

**Why needed:**
- **Directory structure**: Ensures directory exists even if CSVs are gitignored
- Prevents deployment issues if directory doesn't exist

---

## File Dependency Flow

```
User → dashboard.py
         ↓
    ModelRegistry (loads models.yaml)
         ↓
    BedrockEvaluator (uses bedrock_client, tokenizers, timing, json_utils)
         ↓
    Makes API calls to AWS Bedrock
         ↓
    Returns metrics
         ↓
    MetricsLogger (saves to raw_metrics.csv)
         ↓
    ReportGenerator (creates model_comparison.csv)
         ↓
    dashboard.py (displays results using pandas, plotly)
```

---

## Summary by Category

### 🔴 **Critical (Cannot Run Without)**
1. `src/dashboard.py` - Main application
2. `src/evaluator.py` - Core evaluation logic
3. `src/model_registry.py` - Model configuration
4. `configs/models.yaml` - Model definitions
5. `requirements.txt` - Dependencies
6. `src/utils/bedrock_client.py` - AWS connection

### 🟡 **Essential (Core Functionality)**
7. `src/metrics_logger.py` - Data persistence
8. `src/report_generator.py` - Analytics
9. `src/tokenizers.py` - Token counting
10. `src/utils/json_utils.py` - JSON validation
11. `src/utils/timing.py` - Performance measurement

### 🟢 **Supporting (Utilities)**
12. `src/prompt_loader.py` - CSV loading
13. `scripts/run_evaluation.py` - Batch processing
14. `scripts/extract_prompts_from_json.py` - Data conversion
15. `src/__init__.py` - Package marker

### 📚 **Documentation/Config**
16. `README.md` - Project documentation
17. `DEPLOYMENT.md` - Deployment guide
18. `start_dashboard.sh` - Startup script
19. `.gitignore` - Git configuration
20. `configs/settings.yaml` - Settings (if used)

### 💾 **Data Files (Generated)**
21. `data/runs/raw_metrics.csv` - Generated by MetricsLogger
22. `data/runs/model_comparison.csv` - Generated by ReportGenerator
23. `data/runs/.gitkeep` - Directory placeholder

---

## File Size & Complexity

| File | Lines | Complexity | Importance |
|------|-------|------------|------------|
| `dashboard.py` | ~965 | High | ⭐⭐⭐ Critical |
| `evaluator.py` | ~545 | High | ⭐⭐⭐ Critical |
| `model_registry.py` | ~81 | Low | ⭐⭐⭐ Critical |
| `metrics_logger.py` | ~65 | Low | ⭐⭐ Essential |
| `report_generator.py` | ~109 | Medium | ⭐⭐ Essential |
| `tokenizers.py` | ~99 | Medium | ⭐⭐ Essential |
| `json_utils.py` | ~203 | Medium | ⭐ Essential |
| `prompt_loader.py` | ~20 | Low | ⭐ Supporting |

---

## Why Each File is Needed for EC2 Deployment

### Must Have (Application won't work):
- All `src/` Python files (application code)
- `configs/models.yaml` (model configuration)
- `requirements.txt` (dependencies)

### Should Have (Better user experience):
- `DEPLOYMENT.md` (deployment instructions)
- `start_dashboard.sh` (easy startup)
- `README.md` (documentation)

### Nice to Have (Utilities):
- `scripts/` files (batch processing utilities)
- `.gitignore` (clean repository)

### Generated (Created at runtime):
- `data/runs/*.csv` files (created by application)

---

## Quick Reference: What Does What?

- **Run the app**: `streamlit run src/dashboard.py`
- **Configure models**: Edit `configs/models.yaml`
- **Add dependencies**: Update `requirements.txt`
- **Deploy to EC2**: Follow `DEPLOYMENT.md`
- **Batch evaluate**: Use `scripts/run_evaluation.py`
- **View data**: Check `data/runs/raw_metrics.csv`

---

All files are necessary for a complete, production-ready deployment on AWS EC2! 🚀

