# 🔧 Quick Fix: Enable Anthropic Models in AWS Bedrock

## ⚠️ The Error You're Seeing

```
Bedrock API error (ResourceNotFoundException): Model use case details have not been submitted for this account.
Fill out the Anthropic use case details form before using the model.
```

## ✅ Solution: Enable Anthropic Models (5 minutes)

### Step 1: Go to AWS Bedrock Model Access
**Direct Link:** https://console.aws.amazon.com/bedrock/home?region=us-east-2#/modelaccess

Or manually:
1. Go to https://console.aws.amazon.com
2. Search for "Bedrock" in the search bar
3. Click "Amazon Bedrock"
4. Click "Model access" in the left sidebar

### Step 2: Find Anthropic and Enable Models
1. Scroll down to find **"Anthropic"** in the provider list
2. Click **"Request model access"** or **"Enable"** button next to Anthropic
3. You'll see a list of Claude models:
   - Claude 3.7 Sonnet ✅ (you need this one)
   - Claude 3.5 Sonnet
   - Claude 3.5 Haiku
   - etc.

### Step 3: Fill Out the Use Case Form
A form will appear asking:

1. **Use case description**: 
   - Example: "Model evaluation and comparison for cost optimization and performance analysis"
   - Or: "Testing and comparing LLM models for business applications"

2. **Company/Organization**: 
   - Enter your organization name

3. **Accept Terms**: 
   - Check the box to accept terms and conditions

4. **Click "Submit"**

### Step 4: Wait for Approval
- ⏱️ Usually takes **5-15 minutes** (sometimes instant)
- 📧 You'll receive an email confirmation when approved
- ✅ Status will change from "Pending" to "Access granted" in the console

### Step 5: Verify Access
1. Go back to Model Access page
2. Check that Anthropic models show **"Access granted"** status
3. Make sure you're checking the correct region: **us-east-2** (match your `AWS_REGION` in `config.py`)

### Step 6: Wait 1-2 Minutes, Then Try Again
- After approval, wait 1-2 minutes for changes to propagate
- Re-run your evaluation: `python evaluate.py --prompts <your-file>`

## 🌍 Important: Region Must Match

Make sure you enable models in the **same region** as your configuration:
- Your config says: `AWS_REGION = "us-east-2"`
- So enable models in: **us-east-2** region
- If you use multiple regions, enable in each region separately

## 🔄 If You Already Submitted

If you already filled out the form:
1. Wait **15 minutes** (as the error message suggests)
2. Check the Model Access page to see if status changed to "Access granted"
3. If still pending, wait a bit longer (can take up to 30 minutes)
4. Try again after status shows "Access granted"

## ✅ Alternative: Test with Llama First

While waiting for Anthropic access, you can test with Llama (no approval needed):

```bash
# Test with Llama only (no approval needed)
python evaluate.py --prompts <your-file> --models llama-3-2-11b
```

## 📞 Still Having Issues?

1. Check that your AWS credentials have permission to access Bedrock
2. Verify you're using the correct AWS account
3. Make sure your IAM user/role has `bedrock:InvokeModel` permission
4. Check AWS service health status

## 🎯 Quick Checklist

- [ ] Went to AWS Bedrock Model Access page
- [ ] Found "Anthropic" in provider list
- [ ] Clicked "Request model access" or "Enable"
- [ ] Filled out use case form
- [ ] Submitted form
- [ ] Waited 5-15 minutes
- [ ] Verified status shows "Access granted"
- [ ] Checked correct region (us-east-2)
- [ ] Waited 1-2 minutes after approval
- [ ] Re-ran evaluation

---

**Once enabled, the error will disappear and Claude models will work! 🚀**


