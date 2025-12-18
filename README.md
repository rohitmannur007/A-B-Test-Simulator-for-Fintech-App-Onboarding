
# A/B Test Simulator for Fintech App Onboarding

> End-to-end project that ingests A/B experiment data, prepares it, runs statistical tests, visualizes results, and provides an interactive Streamlit dashboard for stakeholders. This repository includes SQL-ready data, Python analysis scripts, visualizations, and a self-healing Streamlit app.

---

## Table of contents

* [Project summary](#project-summary)
* [What’s included](#whats-included)
* [Quickstart (one-line)](#quickstart-one-line)
* [Setup (Mac M2 / pyenv / conda)](#setup-mac-m2--pyenv--conda)
* [How it works — pipeline](#how-it-works---pipeline)
* [Screenshots & interpretation (from your run)](#screenshots--interpretation-from-your-run)
* [Exact SQL queries to run](#exact-sql-queries-to-run)
* [Statistical methods & formulas](#statistical-methods--formulas)
* [Power & sample size (snippet)](#power--sample-size-snippet)
* [Streamlit app explanation](#streamlit-app-explanation)
* [Troubleshooting & common fixes](#troubleshooting--common-fixes)
* [How to present this project (resume / interview)](#how-to-present-this-project-resume--interview)
* [Extensions & next steps](#extensions--next-steps)
* [License](#license)

---

## Project summary

You created an A/B testing system that:

* Loads raw marketing/experiment CSVs (handles messy delimiters & headers),
* Standardizes and processes the data into `ab_cleaned.csv`,
* Loads the processed data into a local SQLite DB (`ab_test.db`),
* Runs statistical comparison (Welch’s t-test), computes lift and confidence intervals,
* Visualizes results and saves a publication-ready chart,
* Provides an interactive Streamlit dashboard that auto-prepares missing processed data and includes a Monte-Carlo A/B simulator.

This is directly relevant to product analytics roles — you demonstrate experiment design, SQL segmentation, statistical testing, and stakeholder communication.

---

## What’s included

```
ab-test-simulator/
├── data/
│   ├── raw/                # control_group.csv, test_group.csv (originals)
│   └── processed/          # ab_cleaned.csv (output)
├── database/
│   └── ab_test.db          # sqlite DB (marketing_ab table)
├── scripts/
│   ├── load_and_prepare.py
│   ├── load_sqlite.py
│   ├── ab_stats.py
│   └── visualize.py
├── streamlit/
│   └── app.py              # interactive dashboard (self-healing)
├── results/
│   ├── summary_metrics.csv
│   └── plots/conversion_comparison.png
├── sql/analysis_queries.sql
├── notebooks/ab_test_report.ipynb
├── requirements.txt
└── README.md
```

---

## Quickstart (one-line)

From project root (`ab-test-simulator`):

```bash
python scripts/load_and_prepare.py && \
python scripts/load_sqlite.py && \
python scripts/ab_stats.py && \
python scripts/visualize.py
```

Then open the dashboard:

```bash
streamlit run streamlit/app.py
```

---

## Setup (Mac M2 / pyenv / conda)

Recommended: use pyenv or Miniforge.

**pyenv (you already use):**

```bash
pyenv install 3.11.5      # if needed
pyenv local 3.11.5
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

**Miniforge (if SciPy wheel issues happen):**

```bash
conda create -n abtest python=3.11 -y
conda activate abtest
pip install -r requirements.txt
```

`requirements.txt` includes:

```
pandas
numpy
scipy
matplotlib
sqlalchemy
streamlit
```

---

## How it works — pipeline (detailed)

1. **Raw ingestion** — the raw CSVs are located at `data/raw/control_group.csv` and `data/raw/test_group.csv`. These can be semicolon (`;`) delimited and have messy column names. The project code accounts for this.
2. **Prepare** — `scripts/load_and_prepare.py` normalizes column names, detects the purchase column (handles `#_of_purchase`, `_of_purchase`, `purchases`), coerces numeric columns, and computes `conversion_rate = purchases / reach`. Output: `data/processed/ab_cleaned.csv`.
3. **SQL load** — `scripts/load_sqlite.py` writes the processed CSV into `database/ab_test.db` as table `marketing_ab`.
4. **Stats** — `scripts/ab_stats.py`:

   * Groups/aggregates data as needed,
   * Computes mean conversion for A & B,
   * Runs Welch’s t-test (unequal variance): `scipy.stats.ttest_ind(B, A, equal_var=False)`,
   * Computes 95% CI for the difference using sample variances (normal approx),
   * Outputs `results/summary_metrics.csv`.
5. **Visualize** — `scripts/visualize.py` creates the bar chart with CIs and saves to `results/plots/conversion_comparison.png`.
6. **Streamlit** — `streamlit/app.py` loads the processed CSV if present, otherwise it auto-runs the prepare step to generate it. It shows dataset preview, metrics, plot, recommendation, and a simulator.

---

## Screenshots & interpretation (from your run)

You uploaded Streamlit screenshots — the dashboard shows:

* **Conversion A** (Control): `0.0061` (≈ 0.61%)
* **Conversion B** (Test): `0.0141` (≈ 1.41%)
* **Lift:** `130.85%` (relative improvement)
* **p-value:** `0.0035` (p < 0.05 → statistically significant)

> **Interpretation (business):** Variant B (simplified onboarding) more than doubles the conversion rate in this dataset; the difference is statistically significant at p ≈ 0.0035. Recommendation: **roll out Variant B**, after verifying assumptions/caveats below.

**How to explain this concisely (one-liner for stakeholders):**
“Variant B produced an absolute uplift of ~0.8 percentage points (from 0.61% → 1.41%), a relative uplift of ~131% (p = 0.0035). I recommend moving forward with Version B and monitoring downstream metrics.”

**Example business impact (quick calc):**
If monthly new users = 100,000 → expected incremental conversions = uplift_abs * monthly_signups = (0.0141 − 0.0061) * 100,000 = 800 additional conversions per month. Multiply by average revenue per conversion to estimate monthly incremental revenue.

---

## Exact SQL queries to run

Open SQLite with `sqlite3 database/ab_test.db` or use a GUI. Useful queries:

**Conversion by variant (sum-based):**

```sql
SELECT
  variant,
  SUM(_of_purchase) as total_purchases,
  SUM(reach) as total_reach,
  ROUND(1.0 * SUM(_of_purchase) / NULLIF(SUM(reach),0), 6) as conversion_rate
FROM marketing_ab
GROUP BY variant;
```

**Per-row averages (for t-test comparisons):**

```sql
SELECT variant, COUNT(*) as rows, ROUND(AVG(conversion_rate), 6) as avg_conv
FROM marketing_ab
GROUP BY variant;
```

**Funnel overview:**

```sql
SELECT variant,
  ROUND(AVG(_of_website_clicks),3) AS avg_clicks,
  ROUND(AVG(_of_add_to_cart),3) AS avg_add_to_cart,
  ROUND(AVG(_of_purchase),3) as avg_purchase
FROM marketing_ab
GROUP BY variant;
```

> Note: column names depend on your processed CSV; inspect `PRAGMA table_info(marketing_ab);` to confirm exact names.

---

## Statistical methods & formulas (exact)

**Welch’s t-test**:

```python
from scipy import stats
t_stat, p_val = stats.ttest_ind(B_values, A_values, equal_var=False, nan_policy='omit')
```

**Absolute & relative uplift**:

```text
diff = meanB - meanA           # absolute uplift (percentage points)
rel_uplift_pct = diff / meanA * 100
```

**95% CI for difference (normal approx)**:

```text
se = sqrt(varA/nA + varB/nB)
ci_low = diff - 1.96*se
ci_high = diff + 1.96*se
```

**When to use proportions methods**: if your aggregation is at *user-level binary outcomes* (converted 0/1), a proportions z-test or chi-square on a 2×2 contingency table is more appropriate. Use `statsmodels.stats.proportion.proportions_ztest` for that.

---

## Power & sample size (quick code snippet)

Use `statsmodels` for power analysis (install `statsmodels` if needed):

```python
from statsmodels.stats.power import NormalIndPower
analysis = NormalIndPower()
# base rate (A), effect size (absolute)
base = 0.0061
target = 0.0141
effect = target - base
# convert to Cohen's h (approx for proportions)
import numpy as np
h = 2 * (np.arcsin(np.sqrt(target)) - np.arcsin(np.sqrt(base)))
power = 0.8
alpha = 0.05
result = analysis.solve_power(effect_size=h, power=power, alpha=alpha, ratio=1.0)
print("Required sample per arm:", int(np.ceil(result)))
```

This gives a sample size per arm to detect the observed uplift with 80% power.

---

## Streamlit app explanation (what to show during demo)

* **Top**: dataset preview: show you understand the raw schema and cleaning steps.
* **Experiment Results**: Conversion A, Conversion B, Lift (%), p-value. Explain significance & business impact.
* **Plot**: clean, clear bar chart with conversion rates — use this as the slide visual.
* **Recommendation banner**: if p < 0.05 AND meanB > meanA show success and rollout recommendation.
* **Simulator**: use it in demo to show how sample size and expected uplift affect statistical significance — run a demo with smaller/larger `n` to show p-value movement.

---

## Troubleshooting & common fixes

* **`FileNotFoundError: ab_cleaned.csv`** — run `python scripts/load_and_prepare.py` first or open Streamlit which auto-prepares if missing.
* **Empty CSV or single-column header** — raw CSV likely uses `;` delimiter; scripts handle `sep=';'`. If using different format, adjust `sep` in the loader.
* **No purchase column found** — the code auto-detects columns that end with `purchase`. Inspect headers with `head -n 1 data/raw/control_group.csv`.
* **SciPy build errors on Mac M1/M2** — use Miniforge/conda and install wheels via conda env.
* **Streamlit stale cache** — restart Streamlit or clear cache (`streamlit cache clear`).

---

## How to present this project (resume / interview)

**Resume bullets (pick 2–3):**

* “Built an end-to-end A/B testing pipeline (Python + SQLite + Streamlit) to evaluate fintech onboarding flows — handled messy production CSVs, ran statistical tests (Welch’s t-test), and produced an interactive dashboard for stakeholders.”
* “Implemented robust data preprocessing with schema detection and a self-healing Streamlit app to ensure reproducibility across environments.”
* “Produced a data-driven recommendation: roll out the simplified onboarding (Variant B) after observing a statistically significant +130% lift in conversion (p = 0.0035).”

**Interview pitch (30s):**

> “I built a full A/B testing system to evaluate onboarding variations: cleaned raw experiment data, ran SQL-based segmentation and Welch’s t-test, visualized conversion lifts, and created a Streamlit dashboard for stakeholders. In my run, the simplified onboarding increased conversion from 0.61% → 1.41% (p = 0.0035), so I recommended rollout.”

---

## Extensions & next steps (to impress)

* Add a **user-level analysis** (per unique user) rather than per-row if available.
* Implement **proportions_ztest** and **chi-square** for binary conversion metrics.
* Run **Bayesian A/B testing** (Beta-Bernoulli) to estimate the posterior probability that B > A.
* Add **cohort retention** analysis (Kaplan–Meier), revenue per user, or LTV.
* Deploy Streamlit on a simple cloud instance (Heroku, Render, Vercel) and add authentication for stakeholders.

---

## Example single-slide summary for stakeholders

**Title:** Simplified Onboarding (Variant B) — Experiment Summary
**Objective:** Increase onboarding completion.
**Key numbers:** Conversion A = 0.61% → Conversion B = 1.41% (Absolute +0.80pp, Relative +130.8%), p = 0.0035.
**Recommendation:** Roll out Variant B.
**Caveats:** Confirm no instrumentation errors; monitor next-week retention and downstream revenue.

---

## License

MIT

---

