"""
DemandDeck -- Step 3: Clean
- Parse job_skills from string to list
- Normalize skill names
- Parse job_posted_date to datetime
- Split into full dataset and salary subset
- Save to data/cleaned/
"""

import ast
import re
from pathlib import Path

import pandas as pd

RAW_PARQUET = Path(__file__).parent.parent / "data" / "raw" / "data_jobs_raw.parquet"
CLEAN_DIR = Path(__file__).parent.parent / "data" / "cleaned"
CLEAN_DIR.mkdir(parents=True, exist_ok=True)

CLEAN_FULL = CLEAN_DIR / "jobs_full.parquet"
CLEAN_SALARY = CLEAN_DIR / "jobs_salary.parquet"
CLEAN_SKILLS_EXPLODED = CLEAN_DIR / "jobs_skills_exploded.parquet"

SKILL_ALIASES = {
    "ms excel": "excel",
    "microsoft excel": "excel",
    "ms word": "word",
    "microsoft word": "word",
    "ms powerpoint": "powerpoint",
    "microsoft powerpoint": "powerpoint",
    "ms sql": "sql server",
    "microsoft sql server": "sql server",
    "mssql": "sql server",
    "t-sql": "sql server",
    "postgresql": "postgres",
    "postgre sql": "postgres",
    "gcp": "google cloud",
    "google cloud platform": "google cloud",
    "aws": "aws",
    "amazon web services": "aws",
    "azure": "azure",
    "microsoft azure": "azure",
    "scikit learn": "scikit-learn",
    "sklearn": "scikit-learn",
    "sci-kit learn": "scikit-learn",
    "tensorflow": "tensorflow",
    "tf": "tensorflow",
    "keras": "keras",
    "pytorch": "pytorch",
    "torch": "pytorch",
    "power bi": "power bi",
    "powerbi": "power bi",
    "tableau": "tableau",
    "looker": "looker",
    "r": "r",
    "python": "python",
    "sql": "sql",
    "java": "java",
    "scala": "scala",
    "spark": "spark",
    "apache spark": "spark",
    "hadoop": "hadoop",
    "kafka": "kafka",
    "apache kafka": "kafka",
    "airflow": "airflow",
    "apache airflow": "airflow",
    "dbt": "dbt",
    "git": "git",
    "github": "git",
    "gitlab": "git",
    "docker": "docker",
    "kubernetes": "kubernetes",
    "k8s": "kubernetes",
    "excel": "excel",
    "word": "word",
    "nosql": "nosql",
    "mongodb": "mongodb",
    "mongo": "mongodb",
    "redshift": "redshift",
    "snowflake": "snowflake",
    "databricks": "databricks",
    "bigquery": "bigquery",
    "sas": "sas",
    "spss": "spss",
    "matlab": "matlab",
    "c++": "c++",
    "c#": "c#",
    "go": "go",
    "rust": "rust",
    "swift": "swift",
    "kotlin": "kotlin",
    "javascript": "javascript",
    "js": "javascript",
    "typescript": "typescript",
    "ts": "typescript",
    "react": "react",
    "node.js": "node.js",
    "nodejs": "node.js",
    "linux": "linux",
    "unix": "linux",
    "bash": "bash",
    "shell": "bash",
    "etl": "etl",
    "machine learning": "machine learning",
    "deep learning": "deep learning",
    "nlp": "nlp",
    "natural language processing": "nlp",
    "computer vision": "computer vision",
    "statistics": "statistics",
    "statistical analysis": "statistics",
}


def normalize_skill(raw: str) -> str:
    s = raw.strip().lower()
    s = re.sub(r"\s+", " ", s)
    return SKILL_ALIASES.get(s, s)


def parse_skills(val) -> list[str] | None:
    if pd.isna(val) or val == "" or val is None:
        return None
    if isinstance(val, list):
        return [normalize_skill(s) for s in val]
    try:
        parsed = ast.literal_eval(val)
        if isinstance(parsed, list):
            return [normalize_skill(s) for s in parsed]
    except (ValueError, SyntaxError):
        pass
    return None


def clean() -> tuple[pd.DataFrame, pd.DataFrame]:
    print("Loading raw parquet...")
    df = pd.read_parquet(RAW_PARQUET)
    print(f"  Raw: {len(df):,} rows x {df.shape[1]} cols")

    # --- Parse date ---
    df["job_posted_date"] = pd.to_datetime(df["job_posted_date"], errors="coerce")

    # --- Parse skills ---
    print("Parsing job_skills...")
    df["skills_list"] = df["job_skills"].apply(parse_skills)
    has_skills = df["skills_list"].notna()
    print(f"  Rows with skills:    {has_skills.sum():>8,}  ({has_skills.mean()*100:.1f}%)")
    print(f"  Rows without skills: {(~has_skills).sum():>8,}  ({(~has_skills).mean()*100:.1f}%)")

    # --- Normalize job_title_short (already clean, just strip) ---
    df["job_title_short"] = df["job_title_short"].str.strip()

    # --- Drop low-value raw cols we won't use downstream ---
    # Keep job_type_skills for reference but don't rely on it
    df_full = df.copy()

    # --- Salary subset: rows with salary_year_avg populated ---
    df_salary = df[df["salary_year_avg"].notna()].copy()
    print(f"\nSalary subset: {len(df_salary):,} rows ({len(df_salary)/len(df)*100:.1f}% of total)")
    print(f"  salary_year_avg mean:   ${df_salary['salary_year_avg'].mean():>9,.0f}")
    print(f"  salary_year_avg median: ${df_salary['salary_year_avg'].median():>9,.0f}")
    print(f"  salary_year_avg min:    ${df_salary['salary_year_avg'].min():>9,.0f}")
    print(f"  salary_year_avg max:    ${df_salary['salary_year_avg'].max():>9,.0f}")

    # --- Skills exploded: one row per (job, skill) for frequency analysis ---
    df_skills_only = df_full[df_full["skills_list"].notna()].copy()
    df_exploded = df_skills_only.explode("skills_list").rename(columns={"skills_list": "skill"})
    df_exploded = df_exploded[df_exploded["skill"].notna() & (df_exploded["skill"] != "")]
    print(f"\nSkills exploded: {len(df_exploded):,} skill-job pairs")
    print(f"  Unique skills: {df_exploded['skill'].nunique():,}")

    # --- Save ---
    df_full.to_parquet(CLEAN_FULL, index=False)
    df_salary.to_parquet(CLEAN_SALARY, index=False)
    df_exploded.to_parquet(CLEAN_SKILLS_EXPLODED, index=False)
    print(f"\nSaved cleaned files:")
    print(f"  {CLEAN_FULL}")
    print(f"  {CLEAN_SALARY}")
    print(f"  {CLEAN_SKILLS_EXPLODED}")

    return df_full, df_salary, df_exploded


def summary(df_full, df_salary, df_exploded):
    print("\n" + "=" * 60)
    print("CLEANED DATASET SUMMARY")
    print("=" * 60)

    print(f"\nFull dataset:   {len(df_full):,} rows x {df_full.shape[1]} cols")
    print(f"Salary subset:  {len(df_salary):,} rows  (has salary_year_avg)")
    print(f"Skills exploded:{len(df_exploded):,} skill-job pairs")

    print("\n-- Date range --")
    print(f"  Earliest posting: {df_full['job_posted_date'].min()}")
    print(f"  Latest posting:   {df_full['job_posted_date'].max()}")

    print("\n-- Job titles (full dataset) --")
    print(df_full["job_title_short"].value_counts().to_string())

    print("\n-- Top 20 skills (by posting count) --")
    top_skills = df_exploded["skill"].value_counts().head(20)
    print(top_skills.to_string())

    print("\n-- Salary by title (salary subset only) --")
    sal_by_title = (
        df_salary.groupby("job_title_short")["salary_year_avg"]
        .agg(["median", "mean", "count"])
        .sort_values("median", ascending=False)
    )
    sal_by_title.columns = ["median_salary", "mean_salary", "n_postings"]
    print(sal_by_title.to_string())

    print("\n-- Top countries (full dataset) --")
    print(df_full["job_country"].value_counts().head(10).to_string())

    print("\n-- Remote vs on-site (full dataset) --")
    print(df_full["job_work_from_home"].value_counts().to_string())

    print("\n" + "=" * 60)


if __name__ == "__main__":
    df_full, df_salary, df_exploded = clean()
    summary(df_full, df_salary, df_exploded)
    print("\nStep 3 complete. Review summary above before Excel export.")
