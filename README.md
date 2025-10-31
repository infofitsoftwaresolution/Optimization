# LLM Model Evaluation Framework

A lightweight Python framework for evaluating and comparing different LLMs hosted on AWS Bedrock. This framework helps you make data-driven decisions about which models perform best for your production use cases.

## 🚀 Features

- ✅ **Multiple Model Support**: Evaluate Claude, Llama, and other Bedrock models side-by-side
- ✅ **Flexible Prompt Loading**: Load prompts from local files (CSV, JSON, TXT) or S3
- ✅ **Comprehensive Metrics**:
  - Input/Output token counts
  - Latency metrics (average, P50, P95, min, max)
  - Cost estimation (USD)
  - JSON validity checking with automatic extraction
  - Automatic retry on invalid JSON
- ✅ **Rich Reporting**: Generates detailed CSV reports with summary statistics and side-by-side comparisons
- ✅ **Enhanced JSON Support**: Automatically extracts JSON from model responses (especially for Llama models)

## 📋 Prerequisites

- Python 3.7 or higher
- AWS Account with Bedrock access
- AWS credentials (Access Key ID and Secret Access Key)

## 🔧 Installation & Setup

**For detailed step-by-step instructions, see [MANUAL_GUIDE.md](MANUAL_GUIDE.md)**

### Quick Setup (3 Steps):

**Step 1:** Clone the repository
```bash
git clone <your-repo-url>
cd bedrock
```

**Step 2:** Install dependencies
```bash
pip install -r requirements.txt
```

**Step 3:** Add your AWS credentials to `config.py`
```python
AWS_ACCESS_KEY_ID = "YOUR_ACCESS_KEY_ID_HERE"
AWS_SECRET_ACCESS_KEY = "YOUR_SECRET_ACCESS_KEY_HERE"
```

**That's it!** You're ready to run. See [MANUAL_GUIDE.md](MANUAL_GUIDE.md) for complete step-by-step instructions.

## 🏃 Quick Start

### Option 1: Use the Included Test File

The repository includes `20251001T000153731Z_e9c5e90710a8738a.json` with sample prompts. Test with 1 prompt:

```bash
python evaluate.py --prompts 20251001T000153731Z_e9c5e90710a8738a.json --max-prompts 1
```

### Option 2: Use Your Own Prompts

**CSV Format:**
```csv
prompt
"Your first prompt here"
"Your second prompt here"
```

**JSON Format (NDJSON - one JSON object per line):**
```json
{"input": {"inputBodyJson": {"messages": [{"role": "user", "content": [{"text": "Your prompt"}]}]}}}
```

**Plain Text:**
```
First prompt here
Second prompt here
```

Then run:
```bash
python evaluate.py --prompts your_prompts.csv
```

## 📊 Usage Examples

### Evaluate All Configured Models

```bash
python evaluate.py --prompts 20251001T000153731Z_e9c5e90710a8738a.json
```

### Evaluate Specific Models

```bash
python evaluate.py --prompts your_prompts.csv --models claude-sonnet llama-3-2-11b
```

### Limit Number of Prompts (for testing)

```bash
python evaluate.py --prompts your_prompts.csv --max-prompts 5
```

### Load Prompts from S3

```bash
python evaluate.py --s3-bucket my-bucket --s3-key prompts.csv
```

### Custom Output Directory

```bash
python evaluate.py --prompts your_prompts.csv --output-dir ./my_results
```

## 📈 Output Files

The framework generates three CSV files in the `results/` directory:

1. **detailed_results_TIMESTAMP.csv**: Full metrics for each prompt/model combination
2. **summary_TIMESTAMP.csv**: Aggregated statistics per model (P50/P95 latency, costs, JSON validity rates)
3. **comparison_TIMESTAMP.csv**: Side-by-side model comparison for each prompt

### Example Summary Output

```
EVALUATION SUMMARY
====================================================================================================
Model                     Avg Lat (ms)    P50 (ms)     P95 (ms)     Avg Cost ($)    JSON Valid %    Total Cost ($)
----------------------------------------------------------------------------------------------------
Claude 3.7 Sonnet         25880.89        25880.89     25880.89     0.023200        100.00        % 0.023200
Llama 3.2 11B Instruct    35030.63        35030.63     35030.63     0.001008        100.00        % 0.001008
====================================================================================================

RECOMMENDATIONS:
  • Most Reliable (JSON): Claude 3.7 Sonnet (100.0% valid)
  • Most Cost-Effective: Llama 3.2 11B Instruct ($0.001008 avg per prompt)
  • Best P95 Latency: Claude 3.7 Sonnet (25880.89ms)
  • Best Overall: Llama 3.2 11B Instruct (balanced cost, latency, and reliability)
```

## ⚙️ Configuration

### Models

Models are pre-configured in `config.py`. Currently includes:
- Claude 3.7 Sonnet (`claude-sonnet`)
- Llama 3.2 11B Instruct (`llama-3-2-11b`)

To add more models, edit `MODELS` and `PRICING` dictionaries in `config.py`.

### Pricing

Pricing is configured per 1K tokens (input/output). Update `PRICING` in `config.py`:

```python
PRICING = {
    "claude-sonnet": {"input": 0.008, "output": 0.024},
    "llama-3-2-11b": {"input": 0.0006, "output": 0.0008},
}
```

## 🛠️ Command-Line Options

```
--prompts PATH          Local path to prompts file (.csv, .json, or .txt)
--s3-bucket BUCKET      S3 bucket name for prompts
--s3-key KEY            S3 key/path for prompts file
--models MODEL ...      Models to evaluate (default: all configured models)
--max-prompts N         Maximum number of prompts to evaluate
--output-dir DIR        Output directory for results (default: results)
--skip-summary          Skip printing summary table to console
```

## 🔍 How It Works

1. **Load Prompts**: The framework loads prompts from your specified source (local file or S3)
2. **Evaluate Models**: For each model, sends prompts to Bedrock API and collects metrics
3. **Extract JSON**: Automatically extracts and validates JSON responses (handles markdown, code blocks, explanatory text)
4. **Retry Logic**: Automatically retries if JSON is invalid (especially for Llama models)
5. **Generate Reports**: Creates comprehensive CSV reports with all metrics and comparisons

## 🐛 Troubleshooting

### AWS Credentials Issues

- Verify your Access Key ID and Secret Access Key in `config.py`
- Ensure your AWS account has Bedrock access
- Check that your region (`AWS_REGION`) is correct

### Model Invocation Errors

- Verify model IDs in `config.py` match your region
- Ensure you have access to the models in Bedrock
- Check AWS IAM permissions for `bedrock:InvokeModel`

### JSON Validation Issues

- The framework automatically extracts JSON from responses
- Check the `json_was_cleaned` column in results to see if extraction was needed
- Llama models often wrap JSON in markdown - this is handled automatically

## 📁 Project Structure

```
bedrock/
├── config.py                  # Configuration (AWS credentials, models, pricing)
├── evaluate.py                # Main CLI script
├── model_evaluator.py         # Model invocation and metrics collection
├── prompt_loader.py           # Prompt loading (local files or S3)
├── results_aggregator.py      # CSV report generation
├── requirements.txt           # Python dependencies
├── README.md                  # This file
└── 20251001T000153731Z_e9c5e90710a8738a.json  # Sample prompts file
```

## 🔐 Security Note

⚠️ **Important**: Never commit your AWS credentials to version control. The `config.py` file with placeholder credentials is included for reference. Always use:
- Environment variables, or
- AWS credentials file (`.aws/credentials`), or
- Update `config.py` locally and add it to `.gitignore`

## 📝 License

This project is provided as-is for evaluation purposes.

## 🤝 Contributing

Feel free to submit issues or pull requests for improvements!
