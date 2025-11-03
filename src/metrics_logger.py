"""Metrics logger: persists per-request metrics to CSV/SQLite."""

from pathlib import Path
from typing import List, Dict, Any, Union
import pandas as pd


class MetricsLogger:
    """Handles logging and persistence of evaluation metrics."""
    
    def __init__(self, output_dir: Union[str, Path]):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.raw_csv_path = self.output_dir / "raw_metrics.csv"
    
    def log_metrics(self, metrics_list: List[Dict[str, Any]]) -> None:
        """
        Log metrics to CSV file.
        
        Args:
            metrics_list: List of metric dictionaries
        """
        if not metrics_list:
            return
        
        df = pd.DataFrame(metrics_list)
        
        # Ensure consistent column order
        expected_columns = [
            "timestamp", "run_id", "model_name", "model_id", "prompt_id",
            "input_tokens", "output_tokens", "latency_ms",
            "json_valid", "error", "status",
            "cost_usd_input", "cost_usd_output", "cost_usd_total"
        ]
        
        # Add input_prompt and response columns if present
        if "input_prompt" in df.columns:
            expected_columns.append("input_prompt")
        if "response" in df.columns:
            expected_columns.append("response")
        
        # If file exists, read existing columns to ensure compatibility
        existing_columns = []
        if self.raw_csv_path.exists():
            try:
                existing_df = pd.read_csv(self.raw_csv_path, nrows=0)  # Just read header
                existing_columns = list(existing_df.columns)
            except Exception:
                # If file is corrupted, we'll recreate it
                existing_columns = []
        
        # Merge expected columns with existing columns
        if existing_columns:
            # Use union of columns to ensure compatibility
            all_columns = list(dict.fromkeys(existing_columns + expected_columns))
        else:
            all_columns = expected_columns
        
        # Reorder and add missing columns
        for col in all_columns:
            if col not in df.columns:
                df[col] = None
        
        # Select columns in the correct order
        df = df[[col for col in all_columns if col in df.columns]]
        
        # Append or create CSV - pandas automatically handles quoting of fields with commas
        header = not self.raw_csv_path.exists()
        df.to_csv(self.raw_csv_path, mode="a", header=header, index=False, escapechar='\\', quoting=1)  # QUOTE_ALL
    
    def get_metrics_df(self) -> pd.DataFrame:
        """Load existing metrics from CSV."""
        if not self.raw_csv_path.exists():
            return pd.DataFrame()
        
        return pd.read_csv(self.raw_csv_path)


def append_metrics_csv(df: pd.DataFrame, out_csv: Union[str, Path]) -> None:
    """Append metrics DataFrame to CSV file."""
    out_path = Path(out_csv)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    header = not out_path.exists()
    df.to_csv(out_path, mode="a", header=header, index=False)


