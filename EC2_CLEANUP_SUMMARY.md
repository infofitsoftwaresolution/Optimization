# Cleanup Summary for AWS EC2 Deployment

## Files Removed ✅

### Documentation Files
- `API_COST_CALCULATION_CHANGES.md` - Development documentation
- `TOKEN_COST_APIS.md` - Development documentation  
- `README_START.md` - Development quick start guide

### Backup/Duplicate Files
- `src/dashboard_fixed.py` - Backup/duplicate file

### Windows-Specific Files
- `start_dashboard.bat` - Windows batch file
- `start_server.ps1` - PowerShell script

### Development/Test Scripts
- `scripts/test_prompt.py` - Test script
- `scripts/list_bedrock_models.py` - Development utility
- `scripts/list_inference_profiles.py` - Development utility
- `scripts/verify_all.py` - Development utility
- `scripts/verify_config.py` - Development utility

### Test Data
- `data/test_prompts.csv` - Test prompts file
- `data/20251001T000153731Z_e9c5e90710a8738a.json` - Test data file

### Cache Directories
- `src/__pycache__/` - Python cache
- `src/utils/__pycache__/` - Python cache
- `scripts/__pycache__/` - Python cache

## Files Kept ✅

### Core Application
- `src/` - All source code
- `configs/` - Configuration files
- `requirements.txt` - Python dependencies
- `README.md` - Main documentation

### Production Scripts
- `scripts/run_evaluation.py` - Production evaluation script
- `scripts/extract_prompts_from_json.py` - Utility script

### Data Structure
- `data/runs/` - Metrics storage directory
- `.gitignore` - Git ignore rules

### Deployment Files
- `start_dashboard.sh` - Linux/EC2 startup script
- `DEPLOYMENT.md` - Deployment guide

## Project Structure After Cleanup

```
AICostOptimizer/
├── configs/
│   ├── models.yaml
│   └── settings.yaml
├── data/
│   └── runs/
│       ├── .gitkeep
│       ├── model_comparison.csv (generated)
│       └── raw_metrics.csv (generated)
├── scripts/
│   ├── extract_prompts_from_json.py
│   └── run_evaluation.py
├── src/
│   ├── dashboard.py
│   ├── evaluator.py
│   ├── metrics_logger.py
│   ├── model_registry.py
│   ├── prompt_loader.py
│   ├── report_generator.py
│   ├── tokenizers.py
│   └── utils/
│       ├── bedrock_client.py
│       ├── json_utils.py
│       └── timing.py
├── .gitignore
├── DEPLOYMENT.md
├── README.md
├── requirements.txt
└── start_dashboard.sh
```

## Next Steps for EC2 Deployment

1. **Transfer files to EC2**:
   ```bash
   scp -r AICostOptimizer/ ubuntu@your-ec2-ip:~/
   ```

2. **SSH into EC2**:
   ```bash
   ssh ubuntu@your-ec2-ip
   ```

3. **Install dependencies**:
   ```bash
   cd ~/AICostOptimizer
   pip3 install -r requirements.txt
   ```

4. **Configure AWS credentials** (if not using IAM role)

5. **Start dashboard**:
   ```bash
   chmod +x start_dashboard.sh
   ./start_dashboard.sh
   ```

See `DEPLOYMENT.md` for complete deployment instructions.

## Notes

- All `__pycache__` directories will be automatically regenerated on first run
- Test data files removed - new data will be generated when running evaluations
- Production scripts (`run_evaluation.py`, `extract_prompts_from_json.py`) kept as they're useful utilities
- Data directory structure preserved with `.gitkeep` file

Project is now ready for AWS EC2 deployment! 🚀

