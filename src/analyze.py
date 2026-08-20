"""
DemandDeck -- Step 5: Analysis
Compute 5 findings from cleaned data. Print all numbers for decisions.md.
"""

from pathlib import Path
import pandas as pd

CLEAN_DIR = Path(__file__).parent.parent / "data" / "cleaned"


def load():
    df_full     = pd.read_parquet(CLEAN_DIR / "jobs_full.parquet")
    df_salary   = pd.read_parquet(CLEAN_DIR / "jobs_salary.parquet")
    df_exploded = pd.read_parquet(CLEAN_DIR / "jobs_skills_exploded.parquet")
    return df_full, df_salary, df_exploded


def finding_1_top_skills(df_exploded):
    """SQL vs Python — who actually leads, and by how much?"""
    print("\n" + "="*60)
    print("FINDING 1: Top skills by posting count (all titles)")
    top = df_exploded["skill"].value_counts().head(25)
    total_postings_with_skills = df_exploded.index.nunique()
    print(f"Base: {total_postings_with_skills:,} postings with skills listed")
    print(top.reset_index().rename(columns={"count":"postings"}).to_string(index=False))
    return top


def finding_2_salary_by_skill(df_exploded):
    """Which skills correlate with higher median salary? (rows with salary_year_avg only)"""
    print("\n" + "="*60)
    print("FINDING 2: Median salary by skill (rows with salary_year_avg, n>=50)")

    # df_exploded already has salary_year_avg from the full dataset
    sal_skills = df_exploded[df_exploded["salary_year_avg"].notna()]
    print(f"  Skill-job pairs with salary: {len(sal_skills):,}")

    by_skill = (
        sal_skills.groupby("skill")["salary_year_avg"]
        .agg(n="count", median="median", mean="mean")
        .query("n >= 50")
        .sort_values("median", ascending=False)
    )
    by_skill["median"] = by_skill["median"].round(0).astype(int)
    by_skill["mean"]   = by_skill["mean"].round(0).astype(int)
    print(by_skill.head(25).to_string())
    print(f"\n...bottom 5 by median salary:")
    print(by_skill.tail(5).to_string())
    return by_skill


def finding_3_excel_rank(df_exploded):
    """Where does Excel rank within Data Analyst postings vs overall?"""
    print("\n" + "="*60)
    print("FINDING 3: Excel rank — overall vs within Data Analyst")

    overall = df_exploded["skill"].value_counts()
    overall_rank = list(overall.index).index("excel") + 1 if "excel" in overall.index else "N/A"
    print(f"  Excel overall rank: #{overall_rank} of {len(overall)} skills  ({overall.get('excel', 0):,} postings)")

    da = df_exploded[df_exploded["job_title_short"] == "Data Analyst"]
    da_skills = da["skill"].value_counts()
    da_rank = list(da_skills.index).index("excel") + 1 if "excel" in da_skills.index else "N/A"
    print(f"  Excel rank in Data Analyst: #{da_rank} of {len(da_skills)} skills  ({da_skills.get('excel', 0):,} postings)")

    print(f"\n  Top 10 skills for Data Analyst:")
    print(da_skills.head(10).reset_index().rename(columns={"count":"postings"}).to_string(index=False))

    return overall_rank, da_rank, da_skills


def finding_4_remote_salary(df_salary):
    """Do remote postings pay more? (salary subset)"""
    print("\n" + "="*60)
    print("FINDING 4: Remote vs on-site salary premium (salary subset)")

    grp = df_salary.groupby("job_work_from_home")["salary_year_avg"].agg(
        n="count", median="median", mean="mean"
    )
    grp["median"] = grp["median"].round(0).astype(int)
    grp["mean"]   = grp["mean"].round(0).astype(int)
    grp.index = grp.index.map({False: "On-Site", True: "Remote"})
    print(grp.to_string())

    remote_med  = df_salary[df_salary["job_work_from_home"]]["salary_year_avg"].median()
    onsite_med  = df_salary[~df_salary["job_work_from_home"]]["salary_year_avg"].median()
    premium     = remote_med - onsite_med
    pct         = premium / onsite_med * 100
    print(f"\n  Remote premium: ${premium:,.0f} ({pct:.1f}% over on-site)")
    return remote_med, onsite_med, premium


def finding_5_seniority_jump(df_salary):
    """How much does seniority pay off? (salary subset)"""
    print("\n" + "="*60)
    print("FINDING 5: Seniority salary jump (salary subset)")

    pairs = [
        ("Data Analyst",     "Senior Data Analyst"),
        ("Data Scientist",   "Senior Data Scientist"),
        ("Data Engineer",    "Senior Data Engineer"),
    ]
    sal_by_title = df_salary.groupby("job_title_short")["salary_year_avg"].median()
    for base, senior in pairs:
        b = sal_by_title.get(base, None)
        s = sal_by_title.get(senior, None)
        if b and s:
            delta = s - b
            pct   = delta / b * 100
            print(f"  {base:<25} ${b:>7,.0f}  ->  {senior:<30} ${s:>7,.0f}  (+${delta:,.0f}, +{pct:.1f}%)")


if __name__ == "__main__":
    print("Loading cleaned data...")
    df_full, df_salary, df_exploded = load()
    print(f"  Full: {len(df_full):,}  Salary: {len(df_salary):,}  Exploded: {len(df_exploded):,}")

    finding_1_top_skills(df_exploded)
    finding_2_salary_by_skill(df_exploded)
    finding_3_excel_rank(df_exploded)
    finding_4_remote_salary(df_salary)
    finding_5_seniority_jump(df_salary)

    print("\n" + "="*60)
    print("Analysis complete.")
