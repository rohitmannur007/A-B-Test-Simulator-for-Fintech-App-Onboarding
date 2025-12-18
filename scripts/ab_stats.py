#!/usr/bin/env python3
"""
Run A/B statistical tests:
- t-test on per-row conversion_rate samples
- compute diff, 95% CI (normal approx using sample variances)
- saves summary_metrics.csv in results/
"""
import os
from pathlib import Path
import pandas as pd
import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
PROCESSED_FP = ROOT / "data" / "processed" / "ab_cleaned.csv"
RESULTS_DIR = ROOT / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

if not PROCESSED_FP.exists():
    raise FileNotFoundError("Processed CSV not found. Run scripts/load_and_prepare.py first.")

df = pd.read_csv(PROCESSED_FP)

# Basic aggregation
grouped = df.groupby("variant").agg(
    rows=("conversion_rate", "count"),
    mean_conv_rate=("conversion_rate", "mean"),
    sum_purchases=("purchase", "sum"),
    sum_reach=("reach", "sum"),
).reset_index()

print("\n=== Aggregated summary ===")
print(grouped.to_string(index=False))

# Per-row samples for statistical test
A_rates = df.loc[df["variant"] == "A", "conversion_rate"].values
B_rates = df.loc[df["variant"] == "B", "conversion_rate"].values

nA = len(A_rates)
nB = len(B_rates)
meanA = A_rates.mean() if nA else 0.0
meanB = B_rates.mean() if nB else 0.0
diff = meanB - meanA

# Welch t-test
t_stat, p_value = stats.ttest_ind(B_rates, A_rates, equal_var=False, nan_policy="omit")

# compute 95% CI for difference using sample variances
varA = np.nanvar(A_rates, ddof=1) if nA > 1 else 0.0
varB = np.nanvar(B_rates, ddof=1) if nB > 1 else 0.0
se = np.sqrt(varA / nA + varB / nB) if nA and nB else np.nan
z = 1.96
ci_low = diff - z * se
ci_high = diff + z * se

# Relative uplift (percent)
rel_uplift_pct = (diff / meanA * 100) if meanA != 0 else np.nan

# Save summary metrics
summary = {
    "variant_A_rows": nA,
    "variant_B_rows": nB,
    "mean_conv_A": meanA,
    "mean_conv_B": meanB,
    "abs_diff_B_minus_A": diff,
    "rel_uplift_pct": rel_uplift_pct,
    "t_statistic": float(t_stat),
    "p_value": float(p_value),
    "ci_low": float(ci_low),
    "ci_high": float(ci_high),
}

summary_df = pd.DataFrame([summary])
summary_csv = RESULTS_DIR / "summary_metrics.csv"
summary_df.to_csv(summary_csv, index=False)
print(f"\nSaved summary metrics → {summary_csv}\n")

# Print human readable
print("=== A/B Test Results ===")
print(f"nA = {nA}, nB = {nB}")
print(f"meanA = {meanA:.6f}, meanB = {meanB:.6f}")
print(f"Absolute difference (B - A) = {diff:.6f}")
print(f"Relative uplift (B vs A) = {rel_uplift_pct:.2f}%")
print(f"Welch t-test: t = {t_stat:.4f}, p = {p_value:.6f}")
print(f"95% CI for (B - A) = [{ci_low:.6f}, {ci_high:.6f}]")
