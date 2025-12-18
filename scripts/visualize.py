#!/usr/bin/env python3
"""
Create a bar chart comparing conversion rates with 95% CI error bars.
Saves to results/plots/conversion_comparison.png
"""
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
PROCESSED_FP = ROOT / "data" / "processed" / "ab_cleaned.csv"
RESULTS_PLOTS = ROOT / "results" / "plots"
RESULTS_PLOTS.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(PROCESSED_FP)

# compute per-variant mean and se using sample variances
groups = df.groupby("variant")["conversion_rate"]
means = groups.mean()
counts = groups.count()
vars_ = groups.var(ddof=1)

se = (vars_ / counts) ** 0.5
ci95 = 1.96 * se

variants = means.index.tolist()
rates = [means[v] for v in variants]
errs = [ci95[v] for v in variants]

fig, ax = plt.subplots(figsize=(6, 5))
x = np.arange(len(variants))
bars = ax.bar(x, rates, tick_label=variants)
ax.errorbar(x, rates, yerr=errs, fmt="none", capsize=8)
ax.set_xlabel("Variant")
ax.set_ylabel("Conversion rate")
ax.set_title("A/B Test: Conversion Rate by Variant (with 95% CI)")
ax.set_ylim(0, max(rates) * 1.6 if max(rates) > 0 else 0.1)

# annotate bar values
for i, v in enumerate(rates):
    ax.text(i, v + (max(errs) * 0.1 if errs else 0.001), f"{v:.4f}", ha="center")

plt.tight_layout()
out_fp = RESULTS_PLOTS / "conversion_comparison.png"
plt.savefig(out_fp, dpi=200)
print(f"Saved plot → {out_fp}")
plt.close(fig)
