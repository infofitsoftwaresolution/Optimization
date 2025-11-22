"""
Diagnostic script to check evaluation data in CSV files and database.
This helps identify why models aren't showing up in the dashboard.
"""

import sys
from pathlib import Path
import pandas as pd
import yaml

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)

from database.connection import get_db_session
from sqlalchemy import text

def check_csv_files():
    """Check what's in the CSV files."""
    print("=" * 60)
    print("Checking CSV Files")
    print("=" * 60)
    
    project_root = Path(__file__).parent.parent
    raw_path = project_root / "data" / "runs" / "raw_metrics.csv"
    agg_path = project_root / "data" / "runs" / "aggregated_metrics.csv"
    
    if not raw_path.exists():
        print(f"❌ raw_metrics.csv not found at: {raw_path}")
        return None, None
    
    if not agg_path.exists():
        print(f"⚠️  aggregated_metrics.csv not found at: {agg_path}")
    
    try:
        raw_df = pd.read_csv(raw_path, on_bad_lines='skip', engine='python')
        print(f"✅ Found raw_metrics.csv with {len(raw_df)} rows")
        
        if 'model_name' in raw_df.columns:
            models = raw_df['model_name'].unique().tolist()
            print(f"\nModels in CSV file ({len(models)}):")
            for model in models:
                model_data = raw_df[raw_df['model_name'] == model]
                count = len(model_data)
                statuses = model_data['status'].value_counts().to_dict()
                print(f"  - {model}: {count} rows, status: {statuses}")
                
                # Show error details if any
                error_rows = model_data[model_data['status'] == 'error']
                if len(error_rows) > 0:
                    print(f"    Error details:")
                    # Check multiple possible error columns
                    for col in ['error', 'error_message', 'response']:
                        if col in error_rows.columns:
                            errors = error_rows[col].dropna().unique()
                            if len(errors) > 0:
                                for err in errors[:2]:  # Show first 2 errors
                                    err_str = str(err)
                                    # Truncate very long errors
                                    if len(err_str) > 200:
                                        err_str = err_str[:200] + "..."
                                    print(f"      [{col}]: {err_str}")
                                break
        else:
            print("⚠️  'model_name' column not found in CSV")
            print(f"   Available columns: {list(raw_df.columns)}")
    except Exception as e:
        print(f"❌ Error reading raw_metrics.csv: {e}")
        raw_df = None
    
    try:
        if agg_path.exists():
            agg_df = pd.read_csv(agg_path, on_bad_lines='skip', engine='python')
            print(f"\n✅ Found aggregated_metrics.csv with {len(agg_df)} rows")
            
            if 'model_name' in agg_df.columns:
                models = agg_df['model_name'].unique().tolist()
                print(f"\nModels in aggregated CSV ({len(models)}):")
                for model in models:
                    print(f"  - {model}")
        else:
            agg_df = None
    except Exception as e:
        print(f"❌ Error reading aggregated_metrics.csv: {e}")
        agg_df = None
    
    return raw_df, agg_df

def check_configured_models():
    """Check what models are configured in YAML."""
    print("\n" + "=" * 60)
    print("Checking Configured Models")
    print("=" * 60)
    
    config_path = Path(__file__).parent.parent / "configs" / "models.yaml"
    if not config_path.exists():
        print(f"❌ Config file not found: {config_path}")
        return []
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    models = config.get('models', [])
    model_names = [m['name'] for m in models]
    
    print(f"Found {len(model_names)} configured models:")
    for name in model_names:
        print(f"  - {name}")
    
    return model_names

def check_database_models():
    """Check what models are in the database."""
    print("\n" + "=" * 60)
    print("Checking Database Models")
    print("=" * 60)
    
    try:
        with get_db_session() as session:
            result = session.execute(text("""
                SELECT m.name, mp.name as provider, 
                       COUNT(em.id) as evaluation_count
                FROM models m
                JOIN model_providers mp ON m.provider_id = mp.id
                LEFT JOIN evaluation_metrics em ON em.model_id = m.id
                GROUP BY m.name, mp.name
                ORDER BY m.name
            """))
            
            rows = result.fetchall()
            if rows:
                print(f"Found {len(rows)} models in database:")
                for row in rows:
                    print(f"  - {row.name} ({row.provider}): {row.evaluation_count} evaluations")
            else:
                print("⚠️  No models found in database")
    except Exception as e:
        print(f"❌ Error querying database: {e}")
        import traceback
        traceback.print_exc()

def compare_and_diagnose():
    """Compare configured models with available data and diagnose issues."""
    print("\n" + "=" * 60)
    print("Diagnosis")
    print("=" * 60)
    
    configured = check_configured_models()
    raw_df, agg_df = check_csv_files()
    check_database_models()
    
    if raw_df is not None and 'model_name' in raw_df.columns:
        csv_models = set(raw_df['model_name'].unique())
        configured_set = set(configured)
        
        missing = configured_set - csv_models
        extra = csv_models - configured_set
        
        if missing:
            print(f"\n⚠️  Configured models with NO data in CSV:")
            for model in missing:
                print(f"  - {model}")
        
        if extra:
            print(f"\nℹ️  Models in CSV but not in config:")
            for model in extra:
                print(f"  - {model}")
        
        if not missing:
            print("\n✅ All configured models have data in CSV files!")
        else:
            print(f"\n💡 To fix: Run evaluations for: {', '.join(missing)}")
            print("   Make sure to select these models in the sidebar before running evaluation.")

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Evaluation Data Diagnostic Tool")
    print("=" * 60)
    print()
    
    compare_and_diagnose()
    
    print("\n" + "=" * 60)
    print("Diagnostic Complete")
    print("=" * 60)

