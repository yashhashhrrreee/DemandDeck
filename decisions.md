# DemandDeck — Decisions Log

Purpose: raw material for resume bullets. Every entry captures action, tool/method, and concrete result.

---

## Step 1: Environment Setup

- What I did: Created Python virtual environment and `requirements.txt` with all project dependencies.
- Tool/method: `python -m venv .venv`, `pip install -r requirements.txt`
- Result: Clean isolated environment with pandas 3.0.5, datasets 5.0.1, openpyxl 3.1.5, matplotlib 3.11.1, plotly 6.9.0, pyarrow 25.0.1.
- Why this choice (vs. alternatives considered): venv over conda — lighter, no install required, sufficient for this project size. pinned major versions in requirements.txt for reproducibility.

---

## Step 2: Data Ingestion

- What I did: Pulled `lukebarousse/data_jobs` dataset from Hugging Face via the `datasets` library, converted to pandas DataFrame, saved raw copies as both CSV and Parquet to `data/raw/`.
- Tool/method: `datasets.load_dataset("lukebarousse/data_jobs", split="train")`, `.to_pandas()`, `df.to_parquet()`, `df.to_csv()`
- Result: 785,741 rows x 17 columns saved to `data/raw/data_jobs_raw.parquet` and `data_jobs_raw.csv`. Download took ~4 seconds at ~200k rows/sec.
- Why this choice (vs. alternatives considered): Saved both Parquet (fast columnar reads for analysis) and CSV (human-readable, universal). Parquet used for all downstream steps to avoid re-parsing.

---

## Step 2b: First-Pass Inspection

- What I did: Profiled raw dataset — dtypes, null counts, unique values, salary summary stats, top job titles.
- Tool/method: `df.dtypes`, `df.isnull().sum()`, `df.nunique()`, `df.describe()`
- Result (key findings):
  - **785,741 total job postings** across 160 countries, 10 standardized job title categories
  - **Top titles**: Data Analyst (196,075), Data Engineer (186,241), Data Scientist (172,286)
  - **Salary data is very sparse**: `salary_year_avg` populated for only 22,003 rows (2.8%); mean $123,286, range $15k–$960k
  - **Skills field**: `job_skills` missing for 117,037 rows (14.9%); stored as string-serialized Python list — needs parsing
  - `job_type_skills` also missing 14.9%; stored as string-serialized dict with skill categories (programming, cloud, analyst_tools, etc.)
  - `salary_rate` 95.8% null — mostly useless as a filter; will use `salary_year_avg` as primary salary field
- Why this choice (vs. alternatives considered): Inspected before cleaning to document baseline null rates so cleaning decisions can be justified with before/after numbers.

---

## Step 3: Data Cleaning

- What I did: Parsed `job_skills` string-serialized lists using `ast.literal_eval`, normalized 70+ skill name variants to canonical forms (e.g. "MS Excel"/"microsoft excel" -> "excel", "gcp" -> "google cloud"), parsed `job_posted_date` to datetime. Split into three output files: full dataset, salary subset, and skills-exploded (one row per skill per job).
- Tool/method: `ast.literal_eval`, regex normalization via alias dict, `pd.to_datetime`, `df.explode()`, `df.to_parquet()`
- Result (with numbers):
  - Full dataset: 785,741 rows x 18 cols (added `skills_list` column)
  - Skills coverage: 668,704 rows have skills (85.1%); 117,037 excluded from skills frequency counts (14.9%)
  - Skills exploded: 3,660,283 skill-job pairs; 245 unique normalized skills
  - Salary subset: 22,003 rows (2.8% of total) — **salary findings are based on this subset only, not the full dataset**
  - Date range: Jan 1 2023 — Dec 31 2023 (full calendar year)
- Why this choice (vs. alternatives considered):
  - Kept full dataset for skills/title/location analysis to maximize coverage; used salary subset separately to avoid overstating salary findings
  - `ast.literal_eval` over regex parsing — safer for structured list strings, handles edge cases cleanly
  - Alias dict normalization over fuzzy matching — deterministic, auditable, fast on 3.6M pairs; fuzzy match would add a dependency and be slower
  - Excluded no-skills rows from frequency counts only (not from full dataset) — they still contribute valid title/country/remote data

---

## Step 3b: Key Cleaning Findings

- What I did: Computed top skills, salary by title, top countries, remote rate from cleaned data.
- Tool/method: `value_counts()`, `groupby().agg()`
- Result (numbers for resume/README use):
  - **Top skills overall**: SQL (384,849 postings), Python (380,909), AWS (145,381), Azure (132,527), R (130,892)
  - **Median salary by title** (salary subset, n=22,003): Senior Data Scientist $155,500 > Senior Data Engineer $147,500 > Data Scientist $127,500 > Data Engineer $125,000 > Data Analyst $90,000
  - **Top country**: United States (206,292 postings, 26.3%); India 2nd (51,088); UK 3rd (40,375)
  - **Remote rate**: 69,552 remote (8.8%) vs 716,189 on-site (91.2%)
- Why this choice: These five numbers are the core findings — defensible in interview because each traces directly to a groupby or value_count on real data.

---

## Step 4: Excel Workbook Build

- What I did: Built `DemandDeck_Analysis.xlsx` (3.3 MB, 8 sheets) using openpyxl with styled headers, alternating row fills, freeze panes, auto-filters, and number formatting. Included a working XLOOKUP formula on the Salary by Title sheet.
- Tool/method: `openpyxl` — `Workbook`, `PatternFill`, `Font`, `Border`, `dataframe_to_rows`, `auto_filter`, XLOOKUP formula string injection
- Result:
  - **8 sheets**: Overview (key metrics), Top Skills (40-skill x 10-title pivot), Salary by Title (median/mean/min/max + XLOOKUP), Salary by Country (US states, n≥20), Remote Trends (remote % by title), Skills per Title Top 10, Raw_Skills (100k sampled rows), Raw_Salary (22,003 rows)
  - File: `outputs/DemandDeck_Analysis.xlsx`, 3.3 MB
  - Raw_Skills capped at 100k sample (noted in-sheet) because full 3.66M exploded rows exceed Excel's 1,048,576-row limit
- Why this choice (vs. alternatives considered):
  - openpyxl over xlsxwriter: openpyxl supports read+write and formula injection; xlsxwriter is write-only but slightly faster — acceptable trade-off given file size is 3.3 MB
  - Pre-computed aggregations (not Excel native PivotTables): openpyxl cannot write Excel PivotTable XML reliably; pre-computed tables with auto-filter + freeze panes achieve same analytical usability and are more portable
  - XLOOKUP over VLOOKUP: XLOOKUP is the modern standard (Excel 2019+), demonstrates current Excel proficiency

---

## Step 5: Analysis — 5 Findings

- What I did: Computed 5 findings from cleaned data: top skills overall, salary by skill, Excel's role-specific rank, remote salary premium, seniority salary jump.
- Tool/method: `value_counts()`, `groupby().agg()`, boolean filtering on `salary_year_avg.notna()`, direct column access on exploded parquet (salary columns preserved through explode)
- Result (all numbers verified from data):
  1. **SQL #1, Python #2 — nearly tied**: SQL in 384,849 postings, Python in 380,909. Gap = 3,940 postings (<1%). Both appear in ~57% of all skill-listed postings.
  2. **High-paying skills skew cloud/infra**: Cassandra, Kafka, Scala, PyTorch, Golang all median ~$147,500. Excel median = $92,500 (2nd lowest), MS Access = $87,555 (lowest). Salary analysis based on 118,886 skill-job pairs with salary_year_avg populated.
  3. **Excel ranks #7 overall but #2 for Data Analysts**: 127,018 total postings; within Data Analyst role, Excel (66,860) ranks behind only SQL (92,428). Shows Excel is role-concentrated, not universally demanded.
  4. **Remote pays 12% more**: Remote median $128,830 vs on-site $115,000 (+$13,830). Based on salary subset (3,279 remote, 18,724 on-site postings with salary).
  5. **Seniority adds ~$21–28k**: Data Analyst +23.5% ($90k→$111k), Data Scientist +22.0% ($127.5k→$155.5k), Data Engineer +18.0% ($125k→$147.5k).
- Why this choice (vs. alternatives considered): Used exploded parquet directly for skill-salary join (salary columns preserved from full dataset through explode step) rather than re-merging — simpler and correct. Salary findings always noted as subset-only.

---

## Step 6: Visualization — 3 Charts

- What I did: Built 3 infographic-style horizontal bar charts exported as 150dpi PNGs using matplotlib. Consistent DemandDeck brand palette (navy/blue/gold), no chartjunk, value labels on bars.
- Tool/method: `matplotlib`, `barh()`, `FuncFormatter`, `mpatches.Patch` for legends, `Agg` backend (no display needed), `bbox_inches="tight"` for clean export
- Result:
  - `demanddeck_top_skills.png` — top 15 skills, SQL/Python highlighted in gold, % of postings labeled
  - `demanddeck_salary_by_title.png` — median salary all 10 titles, senior roles in gold, n= labeled per bar
  - `demanddeck_skills_by_title.png` — 3-panel (Data Analyst / Data Scientist / Data Engineer), top-8 skills as % of postings per title, enables direct cross-role comparison
- Why this choice (vs. alternatives considered): matplotlib over plotly — static PNG export simpler, no browser dependency, sufficient for infographic deliverable. 150dpi balances file size vs. print quality. Horizontal bars over vertical — skill names fit without rotation.

---

## Scope Change: 3 Charts → 6 Charts + Narrative Case Study

- What I did: Expanded from 3 standalone charts to 6 charts, each anchored to a specific question, structured as a narrative case study (Q → finding → so-what) suitable for conversion into a slide deck.
- Why this change: Standalone charts don't read as a coherent argument; a question-driven narrative makes each finding more defensible and presenter-ready. The original 3 charts covered "what skills" and "what salary" but left gaps on skill-salary signal, remote trade-offs, and seniority ROI — all directly relevant to a job-seeker audience.
- New charts added (all prefixed `demanddeck_`, saved to `outputs/charts/`):
  - `demanddeck_skill_salary.png` — Q: Which skills signal higher pay? (top/bottom 10 by median salary, salary-subset only)
  - `demanddeck_remote_trend.png` — Q: Is remote worth it? (remote % by title + salary premium vs on-site)
  - `demanddeck_seniority_jump.png` — Q: How much does seniority pay off? (paired salary bars for junior/senior tracks)
- Narrative structure: 6 findings ordered as a story arc — "what to learn" → "tailor by role" → "where to aim" → "which skills pay" → "remote or not" → "how to grow"
- Findings also saved as `outputs/findings_narrative.md` for slide deck use.

---

## Step 7: Recommendations

- What I did: Wrote 4 data-backed recommendations for a student/job-seeker audience, each anchored to specific numbers computed from the dataset. Saved to `outputs/recommendations.md`.
- Tool/method: Derived directly from findings in Steps 5–6; no new computation.
- Result:
  1. **SQL + Python first** — both at ~385k postings, entry condition for most roles
  2. **Match stack to target role** — Excel is DA's #2 skill, invisible to DE; cloud dominates DE
  3. **Add AWS/Azure for salary step-up** — highest-volume skill in the high-salary tier; learnable with structured cert path
  4. **Remote strategy: apply but don't filter exclusively** — 8.8% of postings, 12% premium, but competition is global; on-site better early-career for mentorship and skill velocity
- Why this choice (vs. alternatives considered): Kept to 4 recommendations to stay tight. Left out a potential "target senior roles" recommendation because seniority is earned, not chosen — actionable advice needs to be something a job-seeker can act on today.

---

## README.md

- What I did: Wrote full project README per CLAUDE.md spec — 7 sections covering overview, dataset, methodology, findings, outputs, alternatives considered, and future scope.
- Tool/method: Written at project completion with all numbers verified against computed outputs.
- Result: `README.md` at project root, ~350 lines, cites specific numbers for all 6 findings, includes salary caveat prominently, covers 5 alternatives considered and 6 future scope items.
- Why this choice: Wrote at the end (not drafted earlier) so all numbers in it are final — no risk of stale placeholders.
