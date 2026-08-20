# DemandDeck

An end-to-end data analytics project analyzing 785,741 real job postings to answer one question: **what does the data job market actually look like in 2023, and what should a job-seeker do about it?**

Built to demonstrate Excel proficiency, infographic-quality data visualization, and data-driven market research — all traceable to real numbers from a real dataset.

---

## Dataset

**Source:** [`lukebarousse/data_jobs`](https://huggingface.co/datasets/lukebarousse/data_jobs) via Hugging Face  
**Size:** 785,741 job postings × 17 columns  
**Contents:** Job title, company, location, country, skills required (as a list), salary (yearly and hourly), remote flag, posting date, schedule type  
**Date range:** January 1 – December 31, 2023  
**Countries:** 160  

> **Salary caveat:** `salary_year_avg` is populated for only 22,003 postings (2.8% of total). All salary figures in this project are drawn from that subset and should be read directionally — not as precise market benchmarks. This is noted explicitly in every chart, sheet, and write-up that cites salary numbers.

---

## Methodology

**Ingest:** Pulled dataset via the `datasets` library, converted to pandas, saved raw copies as both CSV and Parquet to `data/raw/` for reproducibility without re-downloading.

**Clean:** Parsed `job_skills` from string-serialized Python lists using `ast.literal_eval`. Normalized 70+ skill name variants to canonical forms (e.g. "MS Excel" / "microsoft excel" → "excel", "gcp" → "google cloud") via a deterministic alias dictionary. Parsed `job_posted_date` to datetime. Produced three output files:
- `jobs_full.parquet` — all 785,741 rows for title/location/remote analysis
- `jobs_salary.parquet` — 22,003 rows with `salary_year_avg` populated
- `jobs_skills_exploded.parquet` — 3,660,283 skill-job pairs (one row per skill per posting) for frequency analysis

**Analyze:** Computed five core findings using `value_counts()` and `groupby().agg()` on the cleaned data. Salary analysis always runs on the 22,003-row subset and is labeled as such.

**Excel export:** Built `DemandDeck_Analysis.xlsx` using `openpyxl` — 8 styled sheets with freeze panes, auto-filters, alternating row fills, currency formatting, and a working XLOOKUP formula on the Salary by Title sheet. Pre-computed aggregations serve as pivot tables (Excel's native PivotTable XML is not reliably writable via openpyxl).

**Visualize:** Six infographic-style horizontal bar charts built with `matplotlib` (Agg backend, 150 dpi PNG export). Consistent brand palette, value labels on every bar, salary disclaimer on all salary charts.

---

## Findings

### 1. SQL and Python are table stakes — nothing else comes close
SQL appeared in 384,849 postings, Python in 380,909. Together they account for more than 1 in 5 skill mentions across all skill-listed postings. The next tier (AWS at 145k) is less than 40% of SQL's volume. These two skills are the entry condition for the majority of data roles.

### 2. Skill demand is sharply role-specific
Data Analysts require Excel (34% of postings) and Tableau (24%). Data Scientists require Python (66%) and R (35%). Data Engineers require cloud (AWS 33%, Azure 33%) and pipeline tools (Spark 29%). Excel ranks #2 for Data Analysts and doesn't appear in the Data Engineer top 8 at all. A generic "data skills" list is not a strategy.

### 3. Role selection is the largest salary lever
Salary range across roles (salary subset, directional): Business Analyst $85k median → Senior Data Scientist $155.5k median — an $70,500 spread within the same broad "data" labor market.

### 4. Infra and ML skills signal higher pay; BI and productivity tools don't
In the salary subset, skills like Kafka, PyTorch, Scala, Airflow, and Spark cluster around $147,500 median. Excel ($92,500) and MS Access ($87,555) sit at the bottom. The gap between the highest- and lowest-paying skill clusters is ~$60,000.

### 5. Remote is rare (8.8%) but pays a 12% premium
Only 69,552 of 785,741 postings are remote. Remote median salary: $128,830 vs on-site $115,000 (+$13,830, +12.0%). Senior Data Engineer has the highest remote rate at 14.7% — still under 15%.

### 6. Seniority adds ~20% salary across all core data tracks
Data Analyst +23.5% ($90k→$111k), Data Scientist +22.0% ($127.5k→$155.5k), Data Engineer +18.0% ($125k→$147.5k). The percentage gain is strikingly consistent across specializations.

---

## What Was Built

| Output | Description |
|---|---|
| `outputs/DemandDeck_Analysis.xlsx` | 8-sheet Excel workbook: Overview, Top Skills pivot, Salary by Title (with XLOOKUP), Salary by Country (US), Remote Trends, Skills per Title, Raw_Skills (100k sample), Raw_Salary (22k rows) |
| `outputs/charts/demanddeck_top_skills.png` | Top 15 skills by posting count — SQL and Python highlighted |
| `outputs/charts/demanddeck_skills_by_title.png` | Top skills as % of postings for Data Analyst / Scientist / Engineer |
| `outputs/charts/demanddeck_salary_by_title.png` | Median salary all 10 titles, senior roles highlighted, n= per bar |
| `outputs/charts/demanddeck_skill_salary.png` | Top 10 highest vs bottom 5 lowest paying skills |
| `outputs/charts/demanddeck_remote_trend.png` | Remote % by title + remote vs on-site salary comparison |
| `outputs/charts/demanddeck_seniority_jump.png` | Seniority salary jump across Analyst / Scientist / Engineer tracks |
| `outputs/findings_narrative.md` | 6 findings structured as Q → finding → so-what for slide deck use |
| `outputs/recommendations.md` | 4 data-backed recommendations for job seekers |
| `decisions.md` | Full methodology log with actions, tools, and numbers at each step |

---

## Alternatives Considered

**Dataset:** Considered `hugginglearners/data-science-job-salaries` as a secondary source, but the primary dataset (lukebarousse/data_jobs) had 785k postings vs ~40k in the secondary — much richer for skills frequency analysis. Kept as a listed fallback in CLAUDE.md only.

**Tools:** Considered a LangChain-based NLP pipeline to extract skills from raw job descriptions, but `job_skills` was already parsed and normalized in the dataset, making that unnecessary complexity. A direct pandas approach was simpler, faster, and fully auditable.

**Skill normalization:** Considered fuzzy matching (e.g. `rapidfuzz`) for skill name variants, but a deterministic alias dictionary was faster on 3.6M pairs, produced no false matches, and is easier to explain in an interview.

**Excel approach:** Considered xlsxwriter over openpyxl — xlsxwriter is faster and write-only, which is sufficient for export. Chose openpyxl because it supports formula injection (needed for the XLOOKUP demo), is the more commonly cited library, and the 3.3 MB file size means write speed is not a bottleneck.

**Visualization:** Considered Plotly for interactive charts, but static PNGs are more portable (no browser dependency, embeddable anywhere) and sufficient for the infographic deliverable.

---

## Future Scope

- **Live data refresh:** Automate weekly re-pulls from Hugging Face and re-run the full pipeline; track skill demand trends over time
- **Streamlit dashboard:** Wrap the charts and filters into an interactive app — filter by country, title, or skill to explore subsets the static charts don't show
- **Geographic mapping:** Salary and remote-rate choropleth maps by country or US state using the location fields
- **Time-series trend tracking:** The dataset has a full year of posting dates — animate or plot skill demand changes month-by-month across 2023
- **Survey data blend:** Augment with Stack Overflow Developer Survey or Bain/SHRM compensation benchmarks to cross-validate the sparse salary subset
- **Seniority path modeling:** Map the sequence of skills that appear in senior vs non-senior postings for the same title — build a "skills to add for promotion" view

---

*DemandDeck — built Aug 2026. Source data: lukebarousse/data_jobs (Hugging Face). All statistics computed from the dataset — no invented numbers.*
