import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import ttest_ind
from pathlib import Path

# -----------------------------
# Page config
# -----------------------------
st.set_page_config(
    page_title="A/B Test Simulator – Fintech",
    layout="centered"
)

st.title("📊 A/B Test Simulator for Fintech App Onboarding")

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data/processed/ab_cleaned.csv"

# -----------------------------
# Load data
# -----------------------------
@st.cache_data
def load_data():
    return pd.read_csv(DATA_PATH)

df = load_data()

st.subheader("Dataset Preview")
st.dataframe(df.head())

# -----------------------------
# Identify purchase column
# -----------------------------
purchase_col = [c for c in df.columns if c.endswith("purchase")][0]

# -----------------------------
# Metrics
# -----------------------------
A = df[df["variant"] == "A"]["conversion_rate"]
B = df[df["variant"] == "B"]["conversion_rate"]

meanA = A.mean()
meanB = B.mean()
lift = ((meanB - meanA) / meanA) * 100 if meanA != 0 else 0
t_stat, p_value = ttest_ind(B, A, equal_var=False)

st.subheader("📈 Experiment Results")

col1, col2, col3 = st.columns(3)
col1.metric("Conversion A", f"{meanA:.4f}")
col2.metric("Conversion B", f"{meanB:.4f}")
col3.metric("Lift (%)", f"{lift:.2f}%")

st.write(f"**p-value:** `{p_value:.4f}`")

# -----------------------------
# Plot
# -----------------------------
st.subheader("Conversion Rate Comparison")

fig, ax = plt.subplots()
ax.bar(["A", "B"], [meanA, meanB])
ax.set_ylabel("Conversion Rate")
ax.set_title("A/B Test Conversion Rates")

st.pyplot(fig)

# -----------------------------
# Interpretation
# -----------------------------
st.subheader("🧠 Recommendation")

if p_value < 0.05 and meanB > meanA:
    st.success(
        "Variant B (Simplified onboarding) performs significantly better. "
        "Recommend rolling out Version B to all users."
    )
else:
    st.warning(
        "No statistically significant improvement detected. "
        "Recommend continuing the experiment or testing new variants."
    )

# -----------------------------
# BONUS: Interactive Simulator
# -----------------------------
st.subheader("🧪 A/B Test Simulator (Bonus)")

n_users = st.slider("Users per group", 500, 20000, 5000)
base_rate = st.slider("Baseline conversion (A)", 0.01, 0.5, float(meanA))
uplift = st.slider("Expected uplift for B", 0.0, 0.3, 0.05)

if st.button("Run Simulation"):
    sim_A = np.random.binomial(1, base_rate, n_users)
    sim_B = np.random.binomial(1, base_rate + uplift, n_users)

    sim_meanA = sim_A.mean()
    sim_meanB = sim_B.mean()
    sim_lift = ((sim_meanB - sim_meanA) / sim_meanA) * 100

    st.write(f"Simulated A: {sim_meanA:.4f}")
    st.write(f"Simulated B: {sim_meanB:.4f}")
    st.write(f"Lift: {sim_lift:.2f}%")
