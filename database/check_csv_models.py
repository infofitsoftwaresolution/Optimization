#!/usr/bin/env python3
"""Quick script to check what models are actually in the CSV file."""

import sys
from pathlib import Path
import pandas as pd

project_root = Path(__file__).parent.parent
csv_path = project_root / "data" / "runs" / "raw_metrics.csv"

print("=" * 60)
print("CSV File Diagnostic")
print("=" * 60)

if not csv_path.exists():
    print(f"❌ CSV file not found: {csv_path}")
    sys.exit(1)

print(f"✅ CSV file exists: {csv_path}")
print(f"   File size: {csv_path.stat().st_size} bytes")
print(f"   Last modified: {pd.Timestamp.fromtimestamp(csv_path.stat().st_mtime)}")

try:
    df = pd.read_csv(csv_path, on_bad_lines='skip', engine='python')
    print(f"\n✅ Successfully read CSV")
    print(f"   Total rows: {len(df)}")
    
    if 'model_name' in df.columns:
        print(f"\n📊 Models in CSV:")
        model_counts = df['model_name'].value_counts()
        for model, count in model_counts.items():
            print(f"   - {model}: {count} row(s)")
        
        print(f"\n📋 All unique model names:")
        for model in df['model_name'].unique():
            print(f"   - '{model}'")
        
        # Check for status
        if 'status' in df.columns:
            print(f"\n📈 Status breakdown:")
            status_counts = df['status'].value_counts()
            for status, count in status_counts.items():
                print(f"   - {status}: {count} row(s)")
    else:
        print(f"\n⚠️  No 'model_name' column found!")
        print(f"   Available columns: {list(df.columns)}")
        
except Exception as e:
    print(f"❌ Error reading CSV: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)

