"""
DemandDeck — Step 2: Ingest
Pull lukebarousse/data_jobs from Hugging Face, inspect, save raw CSV.
"""

from pathlib import Path

import pandas as pd
from datasets import load_dataset

RAW_DIR = Path(__file__).parent.parent / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

RAW_CSV = RAW_DIR / "data_jobs_raw.csv"
RAW_PARQUET = RAW_DIR / "data_jobs_raw.parquet"


def ingest() -> pd.DataFrame:
    print("Loading dataset from Hugging Face...")
    ds = load_dataset("lukebarousse/data_jobs", split="train")
    df = ds.to_pandas()
    print(f"Downloaded: {len(df):,} rows x {len(df.columns)} columns")

    # Save raw copies
    df.to_csv(RAW_CSV, index=False)
    df.to_parquet(RAW_PARQUET, index=False)
    print(f"Saved raw CSV     -> {RAW_CSV}")
    print(f"Saved raw Parquet -> {RAW_PARQUET}")

    return df


def inspect(df: pd.DataFrame) -> None:
    print("\n" + "=" * 60)
    print("SHAPE")
    print(f"  {df.shape[0]:,} rows  x  {df.shape[1]} columns")

    print("\nCOLUMNS & DTYPES")
    for col, dtype in df.dtypes.items():
        print(f"  {col:<35} {str(dtype)}")

    print("\nNULL COUNTS")
    nulls = df.isnull().sum()
    null_pct = (nulls / len(df) * 100).round(1)
    for col in df.columns:
        if nulls[col] > 0:
            print(f"  {col:<35} {nulls[col]:>7,}  ({null_pct[col]}%)")

    print("\nSAMPLE ROWS (first 3)")
    # Print each row as a dict for readability
    for i, row in df.head(3).iterrows():
        print(f"\n--- Row {i} ---")
        for col, val in row.items():
            # Truncate long values
            display = str(val)
            if len(display) > 120:
                display = display[:117] + "..."
            print(f"  {col:<35} {display}")

    print("\nUNIQUE VALUE COUNTS (key categorical cols)")
    for col in ["job_title_short", "job_location", "job_country", "job_work_from_home"]:
        if col in df.columns:
            print(f"  {col}: {df[col].nunique()} unique")

    print("\nSALARY COLUMNS PREVIEW")
    salary_cols = [c for c in df.columns if "salary" in c.lower()]
    if salary_cols:
        print(df[salary_cols].describe().to_string())
    else:
        print("  No salary columns found")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    df = ingest()
    inspect(df)
    print("\nIngest complete. Review output above before proceeding to clean step.")
