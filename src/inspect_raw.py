"""
DemandDeck -- inspect raw data (loads from local parquet, no download needed).
"""

from pathlib import Path

import pandas as pd

RAW_PARQUET = Path(__file__).parent.parent / "data" / "raw" / "data_jobs_raw.parquet"


def inspect(df: pd.DataFrame) -> None:
    print("=" * 60)
    print("SHAPE")
    print(f"  {df.shape[0]:,} rows  x  {df.shape[1]} columns")

    print("\nCOLUMNS & DTYPES")
    for col, dtype in df.dtypes.items():
        print(f"  {col:<35} {str(dtype)}")

    print("\nNULL COUNTS (non-zero only)")
    nulls = df.isnull().sum()
    null_pct = (nulls / len(df) * 100).round(1)
    found_any = False
    for col in df.columns:
        if nulls[col] > 0:
            print(f"  {col:<35} {nulls[col]:>8,}  ({null_pct[col]}%)")
            found_any = True
    if not found_any:
        print("  (no nulls)")

    print("\nSAMPLE ROWS (first 3)")
    for i, row in df.head(3).iterrows():
        print(f"\n--- Row {i} ---")
        for col, val in row.items():
            display = str(val)
            if len(display) > 120:
                display = display[:117] + "..."
            print(f"  {col:<35} {display}")

    print("\nUNIQUE VALUE COUNTS (key categorical cols)")
    for col in ["job_title_short", "job_location", "job_country", "job_work_from_home"]:
        if col in df.columns:
            print(f"  {col:<35} {df[col].nunique()} unique")

    print("\nTOP 10: job_title_short")
    if "job_title_short" in df.columns:
        print(df["job_title_short"].value_counts().head(10).to_string())

    print("\nSALARY COLUMNS SUMMARY")
    salary_cols = [c for c in df.columns if "salary" in c.lower()]
    if salary_cols:
        print(f"  Salary columns: {salary_cols}")
        print(df[salary_cols].describe().to_string())
    else:
        print("  No salary columns found")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    print(f"Loading from {RAW_PARQUET} ...")
    df = pd.read_parquet(RAW_PARQUET)
    print(f"Loaded: {len(df):,} rows")
    inspect(df)
