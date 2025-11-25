"""
Comprehensive diagnostic script to check why Interactive Analytics isn't showing data.
Checks all possible reasons:
1. CSV file existence and content
2. Status values in data
3. Model name matching
4. Data filtering logic
5. Column presence
"""

import sys
from pathlib import Path
import pandas as pd
import yaml

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

def check_csv_files():
    """Check CSV files for data."""
    print("=" * 80)
    print("1. CHECKING CSV FILES")
    print("=" * 80)
    
    project_root = Path(__file__).parent.parent
    raw_path = project_root / "data" / "runs" / "raw_metrics.csv"
    agg_path = project_root / "data" / "runs" / "model_comparison.csv"
    
    # Check raw CSV
    if not raw_path.exists():
        print(f"❌ raw_metrics.csv NOT FOUND at: {raw_path}")
        return None, None
    else:
        print(f"✅ raw_metrics.csv EXISTS at: {raw_path}")
        print(f"   File size: {raw_path.stat().st_size} bytes")
    
    # Check aggregated CSV
    if not agg_path.exists():
        print(f"⚠️  model_comparison.csv NOT FOUND at: {agg_path}")
    else:
        print(f"✅ model_comparison.csv EXISTS at: {agg_path}")
    
    # Read raw CSV
    try:
        raw_df = pd.read_csv(
            raw_path,
            quoting=1,
            on_bad_lines='skip',
            engine='python'
        )
        print(f"✅ Successfully read raw_metrics.csv: {len(raw_df)} rows")
        print(f"   Columns: {list(raw_df.columns)}")
        
        if len(raw_df) == 0:
            print("❌ CSV file is EMPTY!")
            return None, None
            
    except Exception as e:
        print(f"❌ ERROR reading raw_metrics.csv: {e}")
        return None, None
    
    # Read aggregated CSV
    agg_df = pd.DataFrame()
    if agg_path.exists():
        try:
            agg_df = pd.read_csv(
                agg_path,
                quoting=1,
                on_bad_lines='skip',
                engine='python'
            )
            print(f"✅ Successfully read model_comparison.csv: {len(agg_df)} rows")
        except Exception as e:
            print(f"⚠️  Error reading model_comparison.csv: {e}")
    
    return raw_df, agg_df

def check_status_values(raw_df):
    """Check status values in the data."""
    print("\n" + "=" * 80)
    print("2. CHECKING STATUS VALUES")
    print("=" * 80)
    
    if raw_df is None or raw_df.empty:
        print("❌ No data to check")
        return
    
    if 'status' not in raw_df.columns:
        print("❌ 'status' column NOT FOUND in CSV!")
        print(f"   Available columns: {list(raw_df.columns)}")
        return
    
    status_counts = raw_df['status'].value_counts()
    print(f"✅ Status column found. Value counts:")
    for status, count in status_counts.items():
        print(f"   - '{status}': {count} row(s)")
    
    success_count = len(raw_df[raw_df['status'] == 'success'])
    error_count = len(raw_df[raw_df['status'] == 'error'])
    
    print(f"\n📊 Summary:")
    print(f"   - Success: {success_count} rows")
    print(f"   - Error: {error_count} rows")
    print(f"   - Total: {len(raw_df)} rows")
    
    if success_count == 0:
        print("\n❌ PROBLEM: No rows with status='success'!")
        print("   This is why Interactive Analytics shows no data.")
        print("   All evaluations may have failed.")
        
        # Show error details
        if error_count > 0:
            error_rows = raw_df[raw_df['status'] == 'error']
            print(f"\n   Error details (first 3):")
            for idx, row in error_rows.head(3).iterrows():
                error_msg = row.get('error', 'No error message')
                model = row.get('model_name', 'Unknown')
                print(f"     - {model}: {str(error_msg)[:100]}")
    
    return success_count > 0

def check_model_names(raw_df):
    """Check model names in data."""
    print("\n" + "=" * 80)
    print("3. CHECKING MODEL NAMES")
    print("=" * 80)
    
    if raw_df is None or raw_df.empty:
        print("❌ No data to check")
        return None
    
    if 'model_name' not in raw_df.columns:
        print("❌ 'model_name' column NOT FOUND!")
        return None
    
    models = raw_df['model_name'].unique().tolist()
    print(f"✅ Found {len(models)} unique model(s) in CSV:")
    for model in models:
        count = len(raw_df[raw_df['model_name'] == model])
        success_count = len(raw_df[(raw_df['model_name'] == model) & (raw_df['status'] == 'success')])
        print(f"   - '{model}': {count} total rows, {success_count} success")
    
    return models

def check_configured_models():
    """Check configured models from YAML."""
    print("\n" + "=" * 80)
    print("4. CHECKING CONFIGURED MODELS")
    print("=" * 80)
    
    project_root = Path(__file__).parent.parent
    config_path = project_root / "configs" / "models.yaml"
    
    if not config_path.exists():
        print(f"❌ models.yaml NOT FOUND at: {config_path}")
        return None
    
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        models = config.get('models', [])
        model_names = [m.get('name', '') for m in models if m.get('name')]
        
        print(f"✅ Found {len(model_names)} configured model(s):")
        for name in model_names:
            print(f"   - '{name}'")
        
        return model_names
    except Exception as e:
        print(f"❌ Error reading models.yaml: {e}")
        return None

def check_model_matching(csv_models, configured_models):
    """Check if model names match."""
    print("\n" + "=" * 80)
    print("5. CHECKING MODEL NAME MATCHING")
    print("=" * 80)
    
    if not csv_models or not configured_models:
        print("⚠️  Cannot check matching - missing data")
        return
    
    print("Comparing CSV models with configured models:")
    
    matches = []
    no_matches = []
    
    for csv_model in csv_models:
        csv_lower = str(csv_model).strip().lower()
        matched = False
        
        for config_model in configured_models:
            config_lower = str(config_model).strip().lower()
            
            # Exact match
            if csv_lower == config_lower:
                matches.append((csv_model, config_model))
                matched = True
                break
            
            # Partial match (contains)
            if csv_lower in config_lower or config_lower in csv_lower:
                matches.append((csv_model, config_model))
                matched = True
                break
        
        if not matched:
            no_matches.append(csv_model)
    
    if matches:
        print(f"\n✅ Found {len(matches)} matching model(s):")
        for csv_model, config_model in matches:
            print(f"   - CSV: '{csv_model}' → Config: '{config_model}'")
    
    if no_matches:
        print(f"\n❌ PROBLEM: {len(no_matches)} model(s) in CSV don't match configured models:")
        for model in no_matches:
            print(f"   - '{model}'")
        print("   This could cause filtering to exclude data!")
    
    return len(no_matches) == 0

def check_required_columns(raw_df):
    """Check if required columns exist."""
    print("\n" + "=" * 80)
    print("6. CHECKING REQUIRED COLUMNS")
    print("=" * 80)
    
    if raw_df is None or raw_df.empty:
        print("❌ No data to check")
        return False
    
    required_cols = ['model_name', 'status', 'latency_ms', 'input_tokens', 'output_tokens']
    optional_cols = ['cost_usd_total', 'json_valid', 'response']
    
    missing_required = []
    missing_optional = []
    
    for col in required_cols:
        if col not in raw_df.columns:
            missing_required.append(col)
    
    for col in optional_cols:
        if col not in raw_df.columns:
            missing_optional.append(col)
    
    if missing_required:
        print(f"❌ PROBLEM: Missing required columns: {missing_required}")
        print("   This will cause visualization errors!")
        return False
    
    if missing_optional:
        print(f"⚠️  Missing optional columns: {missing_optional}")
        print("   Some visualizations may not work correctly.")
    
    print(f"✅ All required columns present: {required_cols}")
    return True

def simulate_filtering(raw_df, configured_models):
    """Simulate the filtering logic used in dashboard."""
    print("\n" + "=" * 80)
    print("7. SIMULATING DASHBOARD FILTERING LOGIC")
    print("=" * 80)
    
    if raw_df is None or raw_df.empty:
        print("❌ No data to filter")
        return None
    
    if not configured_models:
        print("⚠️  No configured models - cannot filter")
        return raw_df
    
    print(f"Starting with {len(raw_df)} rows")
    
    # Step 1: Filter by status
    if 'status' in raw_df.columns:
        success_df = raw_df[raw_df['status'] == 'success'].copy()
        print(f"After filtering status='success': {len(success_df)} rows")
        
        if len(success_df) == 0:
            print("❌ PROBLEM: No rows with status='success' after filtering!")
            return None
    else:
        print("⚠️  No 'status' column - skipping status filter")
        success_df = raw_df.copy()
    
    # Step 2: Filter by model name matching
    if 'model_name' in success_df.columns:
        def matches_target_model(data_name, target_list):
            """Simplified matching function."""
            data_clean = str(data_name).strip().lower()
            for target in target_list:
                target_clean = str(target).strip().lower()
                if data_clean == target_clean:
                    return True
                if data_clean in target_clean or target_clean in data_clean:
                    return True
            return False
        
        filtered = success_df[
            success_df['model_name'].apply(
                lambda x: matches_target_model(x, configured_models)
            )
        ].copy()
        
        print(f"After filtering by configured models: {len(filtered)} rows")
        
        if len(filtered) == 0:
            print("❌ PROBLEM: All rows filtered out by model name matching!")
            print(f"   CSV models: {success_df['model_name'].unique().tolist()}")
            print(f"   Configured models: {configured_models}")
            return None
    else:
        print("⚠️  No 'model_name' column - skipping model filter")
        filtered = success_df.copy()
    
    print(f"✅ Final filtered data: {len(filtered)} rows")
    return filtered

def main():
    """Run all diagnostic checks."""
    print("\n" + "=" * 80)
    print("INTERACTIVE ANALYTICS DIAGNOSTIC TOOL")
    print("=" * 80)
    print("\nThis tool checks all possible reasons why Interactive Analytics")
    print("isn't showing data.\n")
    
    # 1. Check CSV files
    raw_df, agg_df = check_csv_files()
    
    # 2. Check status values
    has_success = check_status_values(raw_df)
    
    # 3. Check model names
    csv_models = check_model_names(raw_df)
    
    # 4. Check configured models
    configured_models = check_configured_models()
    
    # 5. Check model matching
    if csv_models and configured_models:
        models_match = check_model_matching(csv_models, configured_models)
    
    # 6. Check required columns
    has_columns = check_required_columns(raw_df)
    
    # 7. Simulate filtering
    if raw_df is not None and configured_models:
        filtered = simulate_filtering(raw_df, configured_models)
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY & RECOMMENDATIONS")
    print("=" * 80)
    
    issues = []
    
    if raw_df is None or raw_df.empty:
        issues.append("❌ CSV file is empty or doesn't exist")
        print("\n🔧 FIX: Run an evaluation to generate data")
    
    if not has_success:
        issues.append("❌ No rows with status='success'")
        print("\n🔧 FIX: Check why evaluations are failing (AWS credentials, model IDs, etc.)")
    
    if not has_columns:
        issues.append("❌ Missing required columns")
        print("\n🔧 FIX: Check metrics_logger.py to ensure all columns are saved")
    
    if csv_models and configured_models and not models_match:
        issues.append("❌ Model names don't match between CSV and config")
        print("\n🔧 FIX: Ensure model names in CSV match exactly with configs/models.yaml")
    
    if not issues:
        print("\n✅ No obvious issues found!")
        print("   The data should be showing. Check:")
        print("   1. Browser cache (try hard refresh: Ctrl+F5)")
        print("   2. Streamlit cache (check if cache needs clearing)")
        print("   3. Check browser console for JavaScript errors")
    else:
        print(f"\n⚠️  Found {len(issues)} issue(s) that need to be fixed:")
        for issue in issues:
            print(f"   {issue}")

if __name__ == "__main__":
    main()

