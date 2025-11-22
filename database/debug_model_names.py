#!/usr/bin/env python3
"""Debug script to compare model names in CSV vs configured models."""

import sys
from pathlib import Path
import pandas as pd
import yaml

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def clean_model_name(name):
    """Clean model name for comparison."""
    if pd.isna(name):
        return ""
    name_str = str(name).strip()
    # Remove tuple formatting if present
    if name_str.startswith("('") and name_str.endswith("',)"):
        name_str = name_str[2:-3]
    elif name_str.startswith("('") and name_str.endswith("')"):
        name_str = name_str[2:-2]
    return name_str.strip()

def main():
    print("=" * 60)
    print("Model Name Debug Tool")
    print("=" * 60)
    
    # Load configured models
    config_path = project_root / "configs" / "models.yaml"
    if not config_path.exists():
        print(f"❌ Config file not found: {config_path}")
        return
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    configured_models = [m['name'] for m in config.get('models', [])]
    print(f"\n✅ Configured models ({len(configured_models)}):")
    for model in configured_models:
        print(f"   - '{model}'")
    
    # Check CSV files
    raw_path = project_root / "data" / "runs" / "raw_metrics.csv"
    agg_path = project_root / "data" / "runs" / "aggregated_metrics.csv"
    
    csv_models = set()
    
    if raw_path.exists():
        try:
            raw_df = pd.read_csv(raw_path, on_bad_lines='skip', engine='python')
            if 'model_name' in raw_df.columns:
                for model_name in raw_df['model_name'].unique():
                    cleaned = clean_model_name(model_name)
                    csv_models.add(cleaned)
                print(f"\n✅ Found {len(raw_df)} rows in raw_metrics.csv")
                print(f"   Unique model names ({len(csv_models)}):")
                for model in sorted(csv_models):
                    print(f"      - '{model}'")
        except Exception as e:
            print(f"❌ Error reading raw_metrics.csv: {e}")
    else:
        print(f"\n⚠️  raw_metrics.csv not found at: {raw_path}")
    
    if agg_path.exists():
        try:
            agg_df = pd.read_csv(agg_path, on_bad_lines='skip', engine='python')
            if 'model_name' in agg_df.columns:
                for model_name in agg_df['model_name'].unique():
                    cleaned = clean_model_name(model_name)
                    csv_models.add(cleaned)
                print(f"\n✅ Found {len(agg_df)} rows in aggregated_metrics.csv")
        except Exception as e:
            print(f"❌ Error reading aggregated_metrics.csv: {e}")
    else:
        print(f"\n⚠️  aggregated_metrics.csv not found at: {agg_path}")
    
    # Compare
    print("\n" + "=" * 60)
    print("COMPARISON")
    print("=" * 60)
    
    missing_in_csv = []
    found_in_csv = []
    
    for configured in configured_models:
        configured_lower = configured.lower().strip()
        found = False
        
        for csv_model in csv_models:
            csv_lower = csv_model.lower().strip()
            if configured_lower == csv_lower:
                found = True
                found_in_csv.append(configured)
                print(f"✅ MATCH: '{configured}' == '{csv_model}'")
                break
        
        if not found:
            # Check for partial matches
            partial_match = None
            for csv_model in csv_models:
                csv_lower = csv_model.lower().strip()
                if configured_lower in csv_lower or csv_lower in configured_lower:
                    partial_match = csv_model
                    break
            
            if partial_match:
                print(f"⚠️  PARTIAL: '{configured}' ~= '{partial_match}'")
                found_in_csv.append(configured)
            else:
                missing_in_csv.append(configured)
                print(f"❌ MISSING: '{configured}' (not found in CSV)")
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Configured models: {len(configured_models)}")
    print(f"Found in CSV: {len(found_in_csv)}")
    print(f"Missing from CSV: {len(missing_in_csv)}")
    
    if missing_in_csv:
        print(f"\n⚠️  Missing models: {', '.join(missing_in_csv)}")
        print("\n💡 This means these models have no evaluation data in the CSV files.")
        print("   Run an evaluation with these models selected to generate data.")
    else:
        print("\n✅ All configured models have data in CSV files!")
        print("   If the dashboard still shows a warning, it's a matching logic issue.")

if __name__ == "__main__":
    main()

