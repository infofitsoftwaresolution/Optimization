# Step-by-Step Manual Guide: Running LLM Model Evaluation

This guide will walk you through running the evaluation framework from start to finish.

## Prerequisites Check

Before starting, make sure you have:
- ✅ Python 3.7 or higher installed
- ✅ AWS Account with Bedrock access enabled
- ✅ AWS Access Key ID and Secret Access Key

**Check Python version:**
```bash
python --version
```
or
```bash
python3 --version
```

## Step 1: Download/Clone the Repository

If you haven't already, download or clone the repository:

```bash
# If using Git
git clone <repository-url>
cd bedrock

# OR download ZIP and extract, then navigate to folder
cd bedrock
```

## Step 2: Install Required Python Packages

Install the required dependencies:

```bash
pip install -r requirements.txt
```

**Expected output:**
```
Collecting boto3>=1.28.0
Collecting botocore>=1.31.0
...
Successfully installed boto3-x.x.x botocore-x.x.x
```

**If you get errors:**
- Try: `pip3 install -r requirements.txt`
- Or: `python -m pip install -r requirements.txt`

## Step 3: Configure AWS Credentials

Open the `config.py` file in any text editor (Notepad, VS Code, etc.).

### 3.1 Find the AWS Credentials Section

Look for these lines (around line 14-16):

```python
AWS_ACCESS_KEY_ID = "YOUR_ACCESS_KEY_ID_HERE"
AWS_SECRET_ACCESS_KEY = "YOUR_SECRET_ACCESS_KEY_HERE"
```

### 3.2 Set Your Credentials

**Option 1: Use Environment Variables (Recommended)**

Create a `.env` file in the project root:
```env
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_REGION=us-east-2
```

**Option 2: Edit config.py directly**

```python
AWS_ACCESS_KEY_ID = "AKIAXXXXXXXXXXXXX"  # Your actual Access Key ID
AWS_SECRET_ACCESS_KEY = "your_secret_key_here"  # Your actual Secret Key
```

**⚠️ SECURITY WARNING:** If you edit `config.py` directly, make sure it's in `.gitignore` or never commit it with real credentials!

### 3.3 (Optional) Update AWS Region

If your AWS region is different, update this line (around line 10):

```python
AWS_REGION = "us-east-2"  # Change to your region (e.g., "us-west-2", "eu-west-1")
```

**Save the file** after making changes.

## Step 4: Verify Your Setup

### 4.1 Check Files Are Present

Make sure these files exist in your directory:
- ✅ `config.py`
- ✅ `evaluate.py`
- ✅ `model_evaluator.py`
- ✅ `prompt_loader.py`
- ✅ `results_aggregator.py`
- ✅ `requirements.txt`
- ✅ `20251001T000153731Z_e9c5e90710a8738a.json` (sample prompts file)

### 4.2 Test Python Can Import Modules

Run this quick test:

```bash
python -c "import boto3; print('✓ boto3 installed successfully')"
```

If you see the checkmark, you're good to go!

## Step 5: Run Your First Evaluation

### Option A: Test with 1 Prompt (Recommended for First Run)

This will test with just 1 prompt to make sure everything works:

```bash
python evaluate.py --prompts 20251001T000153731Z_e9c5e90710a8738a.json --max-prompts 1
```

**What this does:**
- Loads 1 prompt from the included JSON file
- Evaluates both Claude Sonnet and Llama 3.2 11B models
- Shows progress in the terminal
- Generates results in `results/` folder

**Expected output:**
```
Loading prompts...
Loaded 1 prompts

Evaluating Claude 3.7 Sonnet (claude-sonnet) on 1 prompts...
  [1] Processing prompt... ✓ (XXXXms)

Evaluating Llama 3.2 11B Instruct (llama-3-2-11b) on 1 prompts...
  [1] Processing prompt... ✓ (XXXXms)

Generating reports...
Detailed results saved to: results\detailed_results_TIMESTAMP.csv
Summary report saved to: results\summary_TIMESTAMP.csv
Comparison report saved to: results\comparison_TIMESTAMP.csv

====================================================================================================
EVALUATION SUMMARY
====================================================================================================
...
✓ Evaluation complete!
```

**Time:** This typically takes 30-60 seconds for 1 prompt.

### Option B: Run with More Prompts

Once the test works, you can run with more prompts:

```bash
# Test with 5 prompts
python evaluate.py --prompts 20251001T000153731Z_e9c5e90710a8738a.json --max-prompts 5

# Run all prompts (may take longer)
python evaluate.py --prompts 20251001T000153731Z_e9c5e90710a8738a.json
```

## Step 6: View Your Results

After the evaluation completes, check the `results/` folder:

```
results/
├── detailed_results_TIMESTAMP.csv
├── summary_TIMESTAMP.csv
└── comparison_TIMESTAMP.csv
```

### View in Terminal (Linux/Mac):

```bash
# View summary
cat results/summary_*.csv

# View first few lines of detailed results
head -20 results/detailed_results_*.csv
```

### View in Excel/Spreadsheet:

1. Open Excel, Google Sheets, or any spreadsheet application
2. File → Open → Navigate to `results/` folder
3. Open any of the CSV files
4. You'll see columns like:
   - Model name
   - Latency (ms)
   - Cost (USD)
   - JSON validity
   - Token counts

## Step 6.5: View Results in Interactive Dashboard (Optional)

You can also view your results in an interactive Streamlit dashboard with charts and visualizations.

### ⚠️ Important: Streamlit Must Be Started Manually

**Key Point:** Streamlit is NOT running automatically. You MUST start it manually by running a command. Unlike a website that's always available, Streamlit is a server application that you start when you need it, and it runs until you stop it.

**Common Mistake:** Don't try to open `http://localhost:8501` in your browser BEFORE running the Streamlit command - you'll get "connection refused" because nothing is listening on that port yet!

### Launch the Dashboard

**Important:** Make sure you're in the project directory first!

1. Open a terminal/command prompt
2. Navigate to the project directory:
   ```bash
   cd d:\Optimization
   ```
   (or wherever your project is located)

3. Run the Streamlit command:
   ```bash
   streamlit run src/dashboard.py
   ```
   
   **Alternative (if the above doesn't work):**
   ```bash
   python -m streamlit run src/dashboard.py
   ```

**What happens:**
1. **First:** The command starts the Streamlit server (this takes 5-10 seconds)
2. **Then:** You'll see output in the terminal showing it's starting up
3. **Wait for:** The message `You can now view your Streamlit app in your browser.`
4. **Finally:** Open your browser and go to `http://localhost:8501` (or the URL shown in terminal)
5. **Important:** Keep the terminal window open! If you close it, Streamlit stops and you'll get "connection refused" again.

**The dashboard will NOT work if:**
- ❌ You haven't run the `streamlit run` command yet
- ❌ You closed the terminal window where Streamlit is running
- ❌ Streamlit crashed or encountered an error (check the terminal for error messages)

**Expected terminal output:**
```
You can now view your Streamlit app in your browser.
Local URL: http://localhost:8501
Network URL: http://192.168.x.x:8501
```

**Dashboard Features:**
- 📊 **Interactive Charts**: Visualize latency, cost, token usage, and JSON validity
- 📈 **Historical Results**: View and compare all your past evaluations
- 🔍 **Filters**: Filter by model, prompt, or date range
- 📥 **Export**: Download filtered results as CSV
- ⚡ **Real-time Evaluation**: Run new evaluations directly from the dashboard

**To stop the dashboard:**
- Press `Ctrl+C` in the terminal where Streamlit is running
- **Warning:** Once you stop it, the dashboard will be unavailable until you start it again with the command above

### Troubleshooting Dashboard Connection Issues

**Problem: "ERR_CONNECTION_REFUSED" or "localhost refused to connect"**

This means Streamlit isn't running. Here's how to fix it:

1. **Check if Streamlit is installed:**
   ```bash
   python -m streamlit --version
   ```
   If you get an error, install Streamlit:
   ```bash
   pip install streamlit
   ```

2. **Make sure you're in the correct directory:**
   ```bash
   # Windows PowerShell
   cd d:\Optimization
   
   # Windows Command Prompt
   cd d:\Optimization
   
   # Verify you're in the right place
   dir src\dashboard.py
   ```

3. **Run the command from the project root:**
   ```bash
   streamlit run src/dashboard.py
   ```
   
   The terminal should show output like:
   ```
   Collecting usage statistics. To deactivate, set browser.gatherUsageStats to false.
   ...
   You can now view your Streamlit app in your browser.
   ```

4. **Keep the terminal window open** - Streamlit needs to keep running for the dashboard to work

5. **Wait a few seconds** after running the command before opening the browser

6. **Check if another process is using port 8501:**
   - Windows PowerShell:
     ```powershell
     netstat -ano | findstr :8501
     ```
   - If something is using the port, you can either:
     - Stop that process
     - Use a different port: `streamlit run src/dashboard.py --server.port 8502`

**Problem: Streamlit is running but browser shows "ERR_CONNECTION_REFUSED"**

If `netstat` shows port 8501 is LISTENING but you still can't connect:

1. **Try using 127.0.0.1 instead of localhost:**
   - Instead of: `http://localhost:8501`
   - Try: `http://127.0.0.1:8501`

2. **Clear browser cache or try a different browser:**
   - Sometimes browser cache can cause issues
   - Try Chrome, Firefox, or Edge

3. **Check Windows Firewall:**
   - Windows might be blocking localhost connections
   - Try temporarily disabling firewall to test
   - Or add an exception for Python/Streamlit

4. **Verify Streamlit is actually running:**
   ```powershell
   netstat -ano | findstr :8501
   ```
   You should see `LISTENING` status. If not, restart Streamlit.

5. **Try accessing the Network URL instead:**
   - Streamlit shows a "Network URL" when it starts (like `http://192.168.x.x:8501`)
   - Try that URL instead of localhost

6. **Check if antivirus is blocking:**
   - Some antivirus software blocks localhost connections
   - Try adding an exception for Python/Streamlit

**If you still get errors:**
- Make sure all dependencies are installed: `pip install -r requirements.txt`
- Check that `src/dashboard.py` exists in your project directory
- Try running with verbose output: `streamlit run src/dashboard.py --logger.level=debug`
- Check the terminal window where Streamlit is running for any error messages

## Step 7: Understanding the Output

### Summary Report (`summary_TIMESTAMP.csv`)

This shows aggregated statistics:
- **avg_latency_ms**: Average response time
- **p50_latency_ms**: Median response time (50th percentile)
- **p95_latency_ms**: 95th percentile (95% of requests faster than this)
- **avg_cost_usd**: Average cost per prompt
- **valid_json_rate**: Percentage of valid JSON responses (0.0 to 1.0)

### Detailed Results (`detailed_results_TIMESTAMP.csv`)

This shows results for each individual prompt:
- Each row = one prompt evaluated by one model
- Columns include: prompt text, latency, tokens, cost, JSON validity, model output

### Comparison Report (`comparison_TIMESTAMP.csv`)

Side-by-side comparison:
- Each row = one prompt
- Columns show metrics for each model side-by-side
- Easy to compare which model performed better for each prompt

## Common Command Examples

### Evaluate Specific Models Only

```bash
# Only Claude Sonnet
python evaluate.py --prompts 20251001T000153731Z_e9c5e90710a8738a.json --models claude-sonnet

# Only Llama
python evaluate.py --prompts 20251001T000153731Z_e9c5e90710a8738a.json --models llama-3-2-11b

# Both models (default)
python evaluate.py --prompts 20251001T000153731Z_e9c5e90710a8738a.json --models claude-sonnet llama-3-2-11b
```

### Use Your Own Prompt File

```bash
# If you have a CSV file
python evaluate.py --prompts your_prompts.csv --max-prompts 10

# If you have a JSON file
python evaluate.py --prompts your_prompts.json --max-prompts 5
```

### Custom Output Location

```bash
python evaluate.py --prompts 20251001T000153731Z_e9c5e90710a8738a.json --output-dir ./my_results
```

## Troubleshooting Common Issues

### Issue 1: "No module named 'boto3'"

**Solution:**
```bash
pip install boto3 botocore
```

### Issue 2: "Invalid credentials" or AWS errors

**Check:**
1. Did you replace `YOUR_ACCESS_KEY_ID_HERE` in `config.py`?
2. Are your credentials correct?
3. Does your AWS account have Bedrock access?
4. Is your region correct?

**Test credentials:**
```bash
python -c "import boto3; client = boto3.client('sts'); print(client.get_caller_identity())"
```

### Issue 3: "Model not found" or "Access denied"

**Solutions:**
- Verify model IDs in `config.py` are correct for your region
- Check AWS Console → Bedrock → Model access
- Ensure your IAM user has `bedrock:InvokeModel` permission

### Issue 3.5: "Model use case details have not been submitted" (Anthropic Models)

**Error Message:**
```
ResourceNotFoundException: Model use case details have not been submitted for this account. 
Fill out the Anthropic use case details form before using the model.
```

**What this means:**
- Anthropic models (Claude) require you to enable them in AWS Bedrock first
- You must submit a use case form before you can use Claude models
- This is a one-time setup per AWS account

**How to Fix (Step-by-Step):**

1. **Log into AWS Console:**
   - Go to https://console.aws.amazon.com
   - Sign in with your AWS account

2. **Navigate to Amazon Bedrock:**
   - Search for "Bedrock" in the AWS Console search bar
   - Click on "Amazon Bedrock"

3. **Go to Model Access:**
   - In the left sidebar, click on "Model access"
   - Or go directly: https://console.aws.amazon.com/bedrock/home?region=us-east-2#/modelaccess

4. **Enable Anthropic Models:**
   - Look for "Anthropic" in the list of model providers
   - Click "Request model access" or "Enable" next to Anthropic models
   - You'll see models like:
     - Claude 3.5 Sonnet
     - Claude 3.7 Sonnet
     - Claude 3.5 Haiku
     - etc.

5. **Fill Out the Use Case Form:**
   - A form will appear asking for:
     - **Use case description**: Describe what you're using the models for (e.g., "Model evaluation and comparison for cost optimization")
     - **Company/Organization**: Your organization name
     - **Accept Terms**: Check the terms and conditions box
   - Fill out all required fields
   - Click "Submit"

6. **Wait for Approval:**
   - Usually takes 5-15 minutes (sometimes instant)
   - You'll receive an email confirmation when approved
   - The status will change from "Pending" to "Access granted" in the console

7. **Verify Access:**
   - Go back to Model Access in Bedrock
   - Check that Anthropic models show "Access granted" status
   - Make sure you're checking the correct region (should match your `AWS_REGION` in `config.py`)

8. **Try Again:**
   - Once approved, wait 1-2 minutes for the changes to propagate
   - Run your evaluation again

**Important Notes:**
- ⏱️ **Wait Time**: After submitting, wait 15 minutes as mentioned in the error message
- 🌍 **Region**: Make sure you enable models in the same region as your `AWS_REGION` in `config.py` (e.g., `us-east-2`)
- 🔄 **Multiple Regions**: If you use multiple regions, you need to enable models in each region separately
- ✅ **One-Time Setup**: This is a one-time process per AWS account

**Alternative: Use Llama Model (No Approval Required)**

If you need to test immediately, you can use the Llama model which doesn't require use case approval:
- Llama 3.2 11B Instruct (already configured in your setup)

### Issue 4: "File not found" errors

**Check:**
- Are you in the correct directory? (should be `bedrock/`)
- Does the prompt file exist?
- Use full path if needed: `python evaluate.py --prompts /full/path/to/file.json`

### Issue 5: Slow evaluation

**This is normal:**
- Each prompt takes 5-35 seconds depending on the model
- 5 prompts × 2 models = ~2-6 minutes
- Use `--max-prompts` to limit for testing

## Step-by-Step Checklist

Use this checklist to ensure you've done everything:

- [ ] Python 3.7+ installed (`python --version`)
- [ ] Repository downloaded/cloned
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] AWS credentials added to `config.py`
- [ ] AWS region updated (if needed)
- [ ] Test run successful (`--max-prompts 1`)
- [ ] Results files generated in `results/` folder
- [ ] Results viewed and understood

## What's Next?

Once you've successfully run an evaluation:

1. **Experiment with different prompts**: Create your own CSV or JSON files
2. **Compare models**: Review the comparison CSV to see which model performs better
3. **Adjust settings**: Modify `config.py` to add more models or adjust pricing
4. **Analyze results**: Use the detailed CSV for deep analysis in Excel/Python

## Getting Help

If you encounter issues:

1. Check the **Troubleshooting** section above
2. Review the main `README.md` for more details
3. Verify your AWS credentials and permissions
4. Check that all required files are present

## Quick Reference: Complete Command List

```bash
# Install dependencies
pip install -r requirements.txt

# Quick test (1 prompt)
python evaluate.py --prompts 20251001T000153731Z_e9c5e90710a8738a.json --max-prompts 1

# Test with 5 prompts
python evaluate.py --prompts 20251001T000153731Z_e9c5e90710a8738a.json --max-prompts 5

# Full evaluation (all prompts)
python evaluate.py --prompts 20251001T000153731Z_e9c5e90710a8738a.json

# Custom prompts file
python evaluate.py --prompts your_file.csv

# Specific models only
python evaluate.py --prompts 20251001T000153731Z_e9c5e90710a8738a.json --models claude-sonnet

# Custom output directory
python evaluate.py --prompts 20251001T000153731Z_e9c5e90710a8738a.json --output-dir ./custom_results

# Launch Streamlit dashboard (interactive visualization)
streamlit run src/dashboard.py

# View help
python evaluate.py --help
```

That's it! You're ready to evaluate LLM models. 🚀

