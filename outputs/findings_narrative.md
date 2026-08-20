# DemandDeck — Findings Narrative
**Data source:** lukebarousse/data_jobs via Hugging Face  
**Scope:** 785,741 job postings, Jan–Dec 2023, 160 countries  
**Salary note:** Salary data available for only 22,003 postings (2.8%). All salary figures are directional — not precise benchmarks.

---

## Finding 1: SQL and Python are the universal baseline — nothing else comes close

**Question:** What skills does every data professional need?

**Finding:** SQL appeared in 384,849 postings and Python in 380,909 — together they account for more than 1 in 5 skill mentions across 668,704 skill-listed postings. No other skill breaks 150,000. The next tier (AWS at 145k, Azure at 133k, R at 131k) is barely 40% of SQL's volume. The gap between the top 2 and everything else is not marginal — it is structural.

**So what:** SQL and Python are not differentiators; they are table stakes. A candidate who lacks either is disqualified from the majority of data roles before any other qualifications are considered. For a job-seeker, these two skills are the floor, not the ceiling.

---

## Finding 2: Skill demand is role-specific — a generic "data skills" list is a trap

**Question:** Do different data roles actually require different skills?

**Finding:** The three-panel comparison (Data Analyst / Data Scientist / Data Engineer) reveals sharply divergent profiles:
- **Data Analyst**: SQL (47% of postings), Excel (34%), Python (29%), Tableau (24%), Power BI (20%). Visualization and spreadsheet tools dominate.
- **Data Scientist**: Python (66%), R (35%), SQL (46%), SAS (17%), Tableau (17%). Statistics and ML-adjacent language skills dominate.
- **Data Engineer**: SQL (61%), Python (58%), AWS (33%), Azure (33%), Spark (29%). Cloud and pipeline infra dominate. Excel appears in 0% of top-8 skills for this role.

**So what:** "Learn data skills" is not a strategy. Excel proficiency is nearly irrelevant for a Data Engineer but is the #2 most-demanded skill for a Data Analyst. A job-seeker who doesn't target their stack by role is over-preparing for some things and missing others.

---

## Finding 3: Which roles pay what — and where is the floor?

**Question:** What does salary look like across data roles?

**Finding (salary subset, n=22,003, directional only):**

| Role | Median Salary | n |
|---|---|---|
| Senior Data Scientist | $155,500 | 1,690 |
| Senior Data Engineer | $147,500 | 1,591 |
| Data Scientist | $127,500 | 5,922 |
| Data Engineer | $125,000 | 4,500 |
| Senior Data Analyst | $111,175 | 1,131 |
| Machine Learning Engineer | $106,415 | 576 |
| Data Analyst | $90,000 | 5,451 |
| Business Analyst | $85,000 | 610 |

The spread from Business Analyst ($85k) to Senior Data Scientist ($155.5k) is $70,500 — an 83% premium — within the same broad "data" labor market.

**So what:** Role selection is the single largest salary lever a job-seeker has. Moving from Business Analyst to Data Engineer is worth more in expected salary than almost any individual skill upgrade.

---

## Finding 4: The skills that signal higher pay are infra and ML — not BI tools

**Question:** Which skills correlate with higher pay, and which don't?

**Finding (salary subset, skills with n≥50 postings):**

- **Top-paying skills** (all median ~$147–150k): Cassandra ($150k), PyTorch, Scala, Kafka, Redis, Golang, Airflow, Spark, Kubernetes — all infra, pipeline, or deep-ML tools.
- **Lowest-paying skills**: MS Access ($87.5k), Sheets ($90k), Outlook ($90k), Spreadsheet ($92.5k), Excel ($92.5k).

The gap between the highest-paying skill cluster and the lowest is ~$60,000 in median salary.

**So what:** BI tools and office productivity skills (Excel, Sheets, Outlook) appear at the bottom of the salary distribution. The skills that command the highest pay are distributed systems, streaming infra, and ML frameworks. This does not mean Excel is worthless — it's the #2 most-demanded Data Analyst skill (Finding 2) — but it does mean Excel alone is not a salary-growth lever.

---

## Finding 5: Remote jobs are scarce and pay a 12% premium

**Question:** Is remote work common in data, and does it pay more?

**Finding:**
- Only **8.8% of all data job postings** (69,552 of 785,741) are listed as remote — on-site is the strong default.
- Senior Data Engineer has the highest remote rate (14.7%), but even that is under 15%.
- In the salary subset: **remote median = $128,830 vs on-site median = $115,000** — a $13,830 premium (+12.0%).

**So what:** Remote data jobs are a smaller slice of the market than current discourse suggests. The premium exists, but competition for remote roles is inherently higher because the applicant pool is unrestricted by geography. For a job-seeker, remote roles are worth targeting but shouldn't be assumed to be the default.

---

## Finding 6: Seniority adds $21–28k across every data track — consistently

**Question:** How much does gaining seniority actually pay off?

**Finding:**
- Data Analyst → Senior Data Analyst: +$21,175 (+23.5%) — $90k to $111k
- Data Scientist → Senior Data Scientist: +$28,000 (+22.0%) — $127.5k to $155.5k
- Data Engineer → Senior Data Engineer: +$22,500 (+18.0%) — $125k to $147.5k

The percentage gain is strikingly similar across all three tracks (18–23.5%), suggesting seniority carries a roughly consistent premium regardless of specialization.

**So what:** The "senior" title bump is real, large, and consistent. For a job-seeker deciding between lateral moves and investing in depth for a promotion, the data suggests depth pays off at a ~20% salary step-change across all core data tracks.

---

*All numbers computed from lukebarousse/data_jobs (Hugging Face). Salary findings based on 22,003-posting subset — see salary note at top.*
