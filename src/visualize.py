"""
DemandDeck -- Step 6: Visualize
3 infographic-style charts -> outputs/charts/demanddeck_*.png
"""

from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.ticker import FuncFormatter

CLEAN_DIR  = Path(__file__).parent.parent / "data" / "cleaned"
CHART_DIR  = Path(__file__).parent.parent / "outputs" / "charts"
CHART_DIR.mkdir(parents=True, exist_ok=True)

# ---- Brand palette ----
DARK_NAVY  = "#1F3864"
MID_BLUE   = "#2E75B6"
LIGHT_BLUE = "#D6E4F0"
GOLD       = "#C9A84C"
RED_MUTED  = "#C0392B"
GREY_TEXT  = "#555555"
WHITE      = "#FFFFFF"
BG         = "#FAFAFA"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.spines.left": False,
    "axes.grid": True,
    "axes.grid.axis": "x",
    "grid.color": "#E0E0E0",
    "grid.linewidth": 0.8,
    "figure.facecolor": BG,
    "axes.facecolor": BG,
})

FOOTER = "DemandDeck  |  Source: lukebarousse/data_jobs (Hugging Face)  |  785,741 postings, Jan–Dec 2023"


def save(fig, name: str):
    path = CHART_DIR / f"demanddeck_{name}.png"
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=BG)
    plt.close(fig)
    print(f"  Saved -> {path}")
    return path


# ======================================================================
# CHART 1: Top 15 Skills — overall posting count
# ======================================================================
def chart_top_skills(df_exploded: pd.DataFrame):
    top15 = df_exploded["skill"].value_counts().head(15).sort_values()
    total = df_exploded.index.nunique()

    fig, ax = plt.subplots(figsize=(10, 7))
    fig.patch.set_facecolor(BG)

    colors = [GOLD if s in ("sql", "python") else MID_BLUE for s in top15.index]
    bars = ax.barh(top15.index, top15.values, color=colors, height=0.65,
                   edgecolor="white", linewidth=0.5)

    # Value labels
    for bar, val in zip(bars, top15.values):
        pct = val / total * 100
        ax.text(bar.get_width() + 2000, bar.get_y() + bar.get_height()/2,
                f"{val:,}  ({pct:.0f}%)",
                va="center", ha="left", fontsize=8.5, color=GREY_TEXT)

    ax.set_xlim(0, top15.max() * 1.28)
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{int(x/1000)}k"))
    ax.set_xlabel("Number of job postings", fontsize=9, color=GREY_TEXT)
    ax.tick_params(axis="y", labelsize=10)
    ax.tick_params(axis="x", labelsize=8, colors=GREY_TEXT)
    ax.spines["bottom"].set_color("#CCCCCC")

    fig.suptitle("Top 15 In-Demand Skills for Data Jobs (2023)",
                 fontsize=14, fontweight="bold", color=DARK_NAVY, x=0.12, ha="left", y=0.99)
    ax.set_title(f"Based on {total:,} postings with skills listed  |  Gold = top 2",
                 fontsize=8.5, color=GREY_TEXT, loc="left", pad=6)

    legend_patches = [
        mpatches.Patch(color=GOLD, label="SQL / Python (top 2)"),
        mpatches.Patch(color=MID_BLUE, label="Other skills"),
    ]
    ax.legend(handles=legend_patches, fontsize=8.5, loc="lower right",
              framealpha=0.7, edgecolor="#CCCCCC")

    fig.text(0.5, -0.02, FOOTER, ha="center", fontsize=7, color="#999999")
    fig.tight_layout()
    return save(fig, "top_skills")


# ======================================================================
# CHART 2: Median salary by job title (salary subset)
# ======================================================================
def chart_salary_by_title(df_salary: pd.DataFrame):
    sal = (
        df_salary.groupby("job_title_short")["salary_year_avg"]
        .agg(median="median", n="count")
        .sort_values("median")
    )

    fig, ax = plt.subplots(figsize=(10, 6))

    bar_colors = [GOLD if "Senior" in t else MID_BLUE for t in sal.index]
    bars = ax.barh(sal.index, sal["median"], color=bar_colors, height=0.6,
                   edgecolor="white", linewidth=0.5)

    for bar, (title, row) in zip(bars, sal.iterrows()):
        ax.text(bar.get_width() + 1500, bar.get_y() + bar.get_height()/2,
                f"${row['median']:,.0f}  (n={int(row['n']):,})",
                va="center", ha="left", fontsize=8.5, color=GREY_TEXT)

    ax.set_xlim(0, sal["median"].max() * 1.32)
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f"${int(x/1000)}k"))
    ax.set_xlabel("Median annual salary (USD)", fontsize=9, color=GREY_TEXT)
    ax.tick_params(axis="y", labelsize=9.5)
    ax.tick_params(axis="x", labelsize=8, colors=GREY_TEXT)
    ax.spines["bottom"].set_color("#CCCCCC")

    fig.suptitle("Median Annual Salary by Job Title — Data Roles (2023)",
                 fontsize=14, fontweight="bold", color=DARK_NAVY, x=0.12, ha="left", y=0.99)
    ax.set_title(
        f"Salary subset: {len(df_salary):,} postings (2.8% of total) — interpret directionally  |  Gold = senior roles",
        fontsize=8.5, color=RED_MUTED, loc="left", pad=6)

    legend_patches = [
        mpatches.Patch(color=GOLD, label="Senior roles"),
        mpatches.Patch(color=MID_BLUE, label="Non-senior roles"),
    ]
    ax.legend(handles=legend_patches, fontsize=8.5, loc="lower right",
              framealpha=0.7, edgecolor="#CCCCCC")

    fig.text(0.5, -0.02, FOOTER, ha="center", fontsize=7, color="#999999")
    fig.tight_layout()
    return save(fig, "salary_by_title")


# ======================================================================
# CHART 3: Top 8 skills for Data Analyst vs Data Scientist vs Data Engineer
# ======================================================================
def chart_skills_by_title(df_exploded: pd.DataFrame, df_full: pd.DataFrame):
    titles = ["Data Analyst", "Data Scientist", "Data Engineer"]
    colors_map = {
        "Data Analyst":   "#2E75B6",
        "Data Scientist": "#C9A84C",
        "Data Engineer":  "#1F3864",
    }

    # Unique job posting count per title (from full dataset — not exploded pairs)
    title_totals = df_full["job_title_short"].value_counts()

    # Top 8 skills per title by raw count, union skill list
    top_per_title = {}
    union_skills = set()
    for t in titles:
        sub = df_exploded[df_exploded["job_title_short"] == t]["skill"].value_counts().head(8)
        top_per_title[t] = sub
        union_skills.update(sub.index)

    # Order skill_order by Data Analyst count descending
    da_counts = top_per_title["Data Analyst"].reindex(list(union_skills), fill_value=0)
    skill_order = da_counts.sort_values(ascending=False).index.tolist()

    fig, axes = plt.subplots(1, 3, figsize=(14, 6.5), sharey=True)
    fig.text(0.5, 0.98, "Top Skills by Core Data Role (2023)",
             fontsize=14, fontweight="bold", color=DARK_NAVY, ha="center", va="top")
    fig.text(0.5, 0.94, "% = share of job postings for that title listing the skill",
             fontsize=8.5, color=GREY_TEXT, ha="center", va="top")

    for ax, title in zip(axes, titles):
        n_jobs = title_totals.get(title, 1)
        skill_counts = top_per_title[title].reindex(skill_order, fill_value=0)
        # % of job postings requiring each skill
        pct = (skill_counts / n_jobs * 100).round(1)

        bars = ax.barh(skill_order, pct, color=colors_map[title],
                       height=0.65, edgecolor="white", linewidth=0.5)
        for bar, p in zip(bars, pct):
            if p > 0:
                ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
                        f"{p:.0f}%", va="center", ha="left", fontsize=8, color=GREY_TEXT)

        ax.set_title(title, fontsize=11, fontweight="bold",
                     color=colors_map[title], pad=8)
        ax.set_xlabel("% of job postings", fontsize=8.5, color=GREY_TEXT)
        ax.set_xlim(0, pct.max() * 1.35 if pct.max() > 0 else 100)
        ax.tick_params(axis="y", labelsize=9)
        ax.tick_params(axis="x", labelsize=8, colors=GREY_TEXT)
        ax.spines["bottom"].set_color("#CCCCCC")
        ax.text(0.5, -0.10, f"n={n_jobs:,} postings", transform=ax.transAxes,
                ha="center", fontsize=7.5, color=GREY_TEXT)

    fig.subplots_adjust(top=0.88)
    fig.text(0.5, -0.04, FOOTER, ha="center", fontsize=7, color="#999999")
    fig.tight_layout(rect=[0, 0, 1, 0.88])
    return save(fig, "skills_by_title")


# ======================================================================
# MAIN
# ======================================================================
# CHART 4: Which skills signal higher pay?
# Top 10 highest + bottom 5 lowest median salary skills (salary subset)
# ======================================================================
def chart_skill_salary(df_exploded: pd.DataFrame):
    sal_skills = df_exploded[df_exploded["salary_year_avg"].notna()]
    by_skill = (
        sal_skills.groupby("skill")["salary_year_avg"]
        .agg(n="count", median="median")
        .query("n >= 50")
        .sort_values("median", ascending=False)
    )

    top10  = by_skill.head(10)
    bot5   = by_skill.tail(5).sort_values("median", ascending=True)
    combined = pd.concat([bot5, top10]).sort_values("median")

    fig, ax = plt.subplots(figsize=(10, 7))

    colors = [RED_MUTED if s in bot5.index else MID_BLUE for s in combined.index]
    bars = ax.barh(combined.index, combined["median"] / 1000, color=colors,
                   height=0.65, edgecolor="white", linewidth=0.5)

    for bar, (skill, row) in zip(bars, combined.iterrows()):
        ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height() / 2,
                f"${row['median']:,.0f}  (n={int(row['n']):,})",
                va="center", ha="left", fontsize=8.5, color=GREY_TEXT)

    # Divider between bottom and top groups
    divider_y = len(bot5) - 0.5
    ax.axhline(divider_y, color="#CCCCCC", linewidth=1.2, linestyle="--")
    ax.text(combined["median"].max() / 1000 * 0.5, divider_y + 0.15,
            "▲ Higher-paying skills", fontsize=8, color=MID_BLUE, va="bottom")
    ax.text(combined["median"].max() / 1000 * 0.5, divider_y - 0.15,
            "▼ Lower-paying skills", fontsize=8, color=RED_MUTED, va="top")

    ax.set_xlim(0, combined["median"].max() / 1000 * 1.38)
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f"${int(x)}k"))
    ax.set_xlabel("Median annual salary (USD)", fontsize=9, color=GREY_TEXT)
    ax.tick_params(axis="y", labelsize=9.5)
    ax.tick_params(axis="x", labelsize=8, colors=GREY_TEXT)
    ax.spines["bottom"].set_color("#CCCCCC")

    fig.suptitle("Which Skills Signal Higher Pay? (2023)",
                 fontsize=14, fontweight="bold", color=DARK_NAVY, x=0.12, ha="left", y=0.99)
    ax.set_title(
        f"Skills with n≥50 salary postings  |  Red = bottom 5, Blue = top 10  |  "
        f"Salary subset: 22,003 postings — interpret directionally",
        fontsize=8, color=RED_MUTED, loc="left", pad=6,
    )

    legend_patches = [
        mpatches.Patch(color=MID_BLUE, label="Top 10 highest-paying skills"),
        mpatches.Patch(color=RED_MUTED, label="Bottom 5 lowest-paying skills"),
    ]
    ax.legend(handles=legend_patches, fontsize=8.5, loc="lower right",
              framealpha=0.7, edgecolor="#CCCCCC")

    fig.text(0.5, -0.02, FOOTER, ha="center", fontsize=7, color="#999999")
    fig.tight_layout()
    return save(fig, "skill_salary")


# ======================================================================
# CHART 5: Remote vs on-site — prevalence + salary premium
# ======================================================================
def chart_remote_trend(df_full: pd.DataFrame, df_salary: pd.DataFrame):
    # Remote % by title (full dataset)
    remote_pct = (
        df_full.groupby("job_title_short")["job_work_from_home"]
        .mean() * 100
    ).sort_values(ascending=False)

    # Remote salary premium (salary subset)
    remote_sal  = df_salary[df_salary["job_work_from_home"]]["salary_year_avg"].median()
    onsite_sal  = df_salary[~df_salary["job_work_from_home"]]["salary_year_avg"].median()

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.5))

    # Left: remote % by title
    colors1 = [GOLD if pct >= 15 else MID_BLUE for pct in remote_pct.values]
    bars1 = ax1.barh(remote_pct.index, remote_pct.values, color=colors1,
                     height=0.65, edgecolor="white", linewidth=0.5)
    for bar, pct in zip(bars1, remote_pct.values):
        ax1.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height() / 2,
                 f"{pct:.1f}%", va="center", ha="left", fontsize=8.5, color=GREY_TEXT)
    ax1.set_xlim(0, remote_pct.max() * 1.45)
    ax1.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{x:.0f}%"))
    ax1.set_xlabel("% of postings that are remote", fontsize=9, color=GREY_TEXT)
    ax1.set_title("Remote Posting Rate by Title\n(full dataset: 785,741 postings)",
                  fontsize=10, fontweight="bold", color=DARK_NAVY, pad=8)
    ax1.tick_params(axis="y", labelsize=9)
    ax1.tick_params(axis="x", labelsize=8, colors=GREY_TEXT)
    ax1.spines["bottom"].set_color("#CCCCCC")
    legend1 = [
        mpatches.Patch(color=GOLD,     label="≥15% remote"),
        mpatches.Patch(color=MID_BLUE, label="<15% remote"),
    ]
    ax1.legend(handles=legend1, fontsize=8, loc="lower right", framealpha=0.7)

    # Right: overall remote vs on-site salary comparison
    categories = ["On-Site", "Remote"]
    salaries   = [onsite_sal / 1000, remote_sal / 1000]
    ns         = [
        int(df_salary[~df_salary["job_work_from_home"]].shape[0]),
        int(df_salary[df_salary["job_work_from_home"]].shape[0]),
    ]
    bar_colors2 = [MID_BLUE, GOLD]
    bars2 = ax2.bar(categories, salaries, color=bar_colors2,
                    width=0.45, edgecolor="white", linewidth=0.5)

    for bar, sal, n in zip(bars2, salaries, ns):
        # Label inside bar bottom to avoid crowding
        ax2.text(bar.get_x() + bar.get_width() / 2, bar.get_height() / 2,
                 f"${sal:.0f}k\n(n={n:,})",
                 ha="center", va="center", fontsize=10, fontweight="bold", color=WHITE)

    # Annotation: premium — text above remote bar
    premium = remote_sal - onsite_sal
    pct_prem = premium / onsite_sal * 100
    ax2.text(1, remote_sal / 1000 + 2,
             f"+${premium/1000:.1f}k (+{pct_prem:.1f}%)\nvs on-site",
             ha="center", va="bottom", fontsize=10, fontweight="bold", color=GOLD)

    ax2.set_ylim(0, max(salaries) * 1.3)
    ax2.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f"${int(x)}k"))
    ax2.set_ylabel("Median annual salary (USD)", fontsize=9, color=GREY_TEXT)
    ax2.set_title(
        "Remote vs On-Site Salary\n(salary subset: 22,003 postings — directional only)",
        fontsize=10, fontweight="bold", color=DARK_NAVY, pad=8,
    )
    ax2.tick_params(axis="x", labelsize=10)
    ax2.tick_params(axis="y", labelsize=8, colors=GREY_TEXT)
    ax2.spines["left"].set_color("#CCCCCC")
    ax2.spines["bottom"].set_color("#CCCCCC")
    ax2.grid(axis="y", color="#E0E0E0", linewidth=0.8)
    ax2.set_axisbelow(True)

    fig.suptitle("Remote Work: How Common Is It, and Does It Pay More? (2023)",
                 fontsize=13, fontweight="bold", color=DARK_NAVY, y=1.01)
    fig.text(0.5, -0.03, FOOTER, ha="center", fontsize=7, color="#999999")
    fig.tight_layout()
    return save(fig, "remote_trend")


# ======================================================================
# CHART 6: Seniority salary jump — junior vs senior by track
# ======================================================================
def chart_seniority_jump(df_salary: pd.DataFrame):
    pairs = [
        ("Data Analyst",   "Senior Data Analyst"),
        ("Data Scientist", "Senior Data Scientist"),
        ("Data Engineer",  "Senior Data Engineer"),
    ]
    sal = df_salary.groupby("job_title_short")["salary_year_avg"].agg(
        median="median", n="count"
    )

    labels_junior = [p[0] for p in pairs]
    labels_senior = [p[1] for p in pairs]
    vals_junior   = [sal.loc[j, "median"] / 1000 for j in labels_junior]
    vals_senior   = [sal.loc[s, "median"] / 1000 for s in labels_senior]
    n_junior      = [int(sal.loc[j, "n"]) for j in labels_junior]
    n_senior      = [int(sal.loc[s, "n"]) for s in labels_senior]
    deltas        = [sv - jv for jv, sv in zip(vals_junior, vals_senior)]
    pcts          = [d / j * 100 for d, j in zip(deltas, vals_junior)]

    x = range(len(pairs))
    width = 0.35

    fig, ax = plt.subplots(figsize=(11, 6))

    bars_j = ax.bar([xi - width/2 for xi in x], vals_junior, width,
                    color=MID_BLUE, label="Non-Senior", edgecolor="white", linewidth=0.5)
    bars_s = ax.bar([xi + width/2 for xi in x], vals_senior, width,
                    color=GOLD, label="Senior", edgecolor="white", linewidth=0.5)

    # Value labels + n=
    for bar, val, n in zip(bars_j, vals_junior, n_junior):
        # Labels inside bars
        ax.text(bar.get_x() + bar.get_width()/2, val / 2,
                f"${val:.0f}k\n(n={n:,})", ha="center", va="center",
                fontsize=8.5, color=WHITE, fontweight="bold")
    for bar, val, n in zip(bars_s, vals_senior, n_senior):
        ax.text(bar.get_x() + bar.get_width()/2, val / 2,
                f"${val:.0f}k\n(n={n:,})", ha="center", va="center",
                fontsize=8.5, color=DARK_NAVY, fontweight="bold")

    # Delta annotations well above each pair
    for i, (delta, pct) in enumerate(zip(deltas, pcts)):
        mid_x = i
        mid_y = max(vals_junior[i], vals_senior[i]) + 14
        ax.text(mid_x, mid_y, f"+${delta:.0f}k  (+{pct:.1f}%)",
                ha="center", va="bottom", fontsize=10, fontweight="bold", color=GOLD)

    short_labels = ["Data Analyst", "Data Scientist", "Data Engineer"]
    ax.set_xticks(list(x))
    ax.set_xticklabels(short_labels, fontsize=11, fontweight="bold", color=DARK_NAVY)
    ax.set_ylim(0, max(vals_senior) * 1.38)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: f"${int(y)}k"))
    ax.set_ylabel("Median annual salary (USD)", fontsize=9, color=GREY_TEXT)
    ax.tick_params(axis="y", labelsize=8, colors=GREY_TEXT)
    ax.spines["bottom"].set_color("#CCCCCC")
    ax.spines["left"].set_color("#CCCCCC")
    ax.legend(fontsize=10, loc="upper left", framealpha=0.7, edgecolor="#CCCCCC")

    fig.suptitle("How Much Does Seniority Pay Off? (2023)",
                 fontsize=14, fontweight="bold", color=DARK_NAVY, x=0.12, ha="left", y=1.01)
    ax.set_title(
        "Salary subset: 22,003 postings (2.8% of total) — interpret directionally",
        fontsize=8.5, color=RED_MUTED, loc="left", pad=6,
    )

    fig.text(0.5, -0.03, FOOTER, ha="center", fontsize=7, color="#999999")
    fig.tight_layout()
    return save(fig, "seniority_jump")


# ======================================================================
if __name__ == "__main__":
    print("Loading cleaned data...")
    df_full     = pd.read_parquet(CLEAN_DIR / "jobs_full.parquet")
    df_salary   = pd.read_parquet(CLEAN_DIR / "jobs_salary.parquet")
    df_exploded = pd.read_parquet(CLEAN_DIR / "jobs_skills_exploded.parquet")

    print("Building charts...")
    chart_top_skills(df_exploded)
    chart_skills_by_title(df_exploded, df_full)
    chart_salary_by_title(df_salary)
    chart_skill_salary(df_exploded)
    chart_remote_trend(df_full, df_salary)
    chart_seniority_jump(df_salary)
    print("All 6 charts saved.")
