import json, re
import numpy as np
import plotly.graph_objects as go
import streamlit as st
import app_utils as U

U.setup("Task 1 - Title keywords vs pay", "💰", "Which words in a job title go with higher or lower advertised pay?")
meta = json.loads((U.REPORTS / "task1_meta.json").read_text())
kind = st.radio("Pay type", ["Hourly rate (USD/h)", "Fixed-price budget (USD)"], horizontal=True)
key = "hourly_mid" if kind.startswith("Hourly") else "budget"
res = U.read_csv(f"task1_{key}_keyword_effects.csv")

c = st.columns(3)
c[0].metric("Jobs analysed", f"{meta[key]['n_jobs']:,}")
c[1].metric("Keywords tested", f"{len(res):,}")
c[2].metric("Title-only model R²", f"{meta[key]['ridge_cv_r2']:.2f}", help="Share of variance in log pay explained by title keywords alone (5-fold CV Ridge).")

n = st.slider("Keywords to show per side", 5, 30, 12)
only_sig = st.checkbox("Only statistically significant (Bonferroni p < 0.01)", True)
r = res[res.significant] if only_sig else res
r = r.sort_values("corr_log_pay")
show = r.tail(n).tail(n).iloc[::-1], r.head(n)
fig = go.Figure(go.Bar(x=list(show[0].corr_log_pay) + list(show[1].corr_log_pay)[::-1], y=list(show[0].keyword) + list(show[1].keyword)[::-1], orientation="h",
                       marker_color=["#2a9d8f"] * len(show[0]) + ["#e76f51"] * len(show[1])))
fig.update_layout(height=max(400, 22 * 2 * n), yaxis=dict(autorange="reversed"), xaxis_title="correlation with log pay", margin=dict(l=0, r=0, t=10, b=0))
st.plotly_chart(fig, width="stretch")
st.dataframe(r.sort_values("corr_log_pay", ascending=False)[["keyword", "n_jobs", "median_with", "median_without", "corr_log_pay", "p_adj"]], width="stretch", hide_index=True, height=300)

st.subheader("Look up any keyword")
df = U.load_df()
kw = st.text_input("Word or phrase in the title", "shopify").strip().lower()
if kw:
    m = df.title_clean.str.contains(rf"\b{re.escape(kw)}\b", regex=True)
    if m.sum() == 0:
        st.warning("No postings contain that word.")
    else:
        rows = []
        for lab, col, sub in (("Hourly rate (USD/h)", "hourly_mid", df.is_hourly), ("Fixed budget (USD)", "budget", ~df.is_hourly)):
            a, b = df.loc[m & sub, col].dropna(), df.loc[~m & sub, col].dropna()
            rows.append({"pay": lab, "postings with word": len(a), "median with": a.median(), "median without": b.median(), "ratio": a.median() / b.median() if len(a) else np.nan})
        st.caption(f"{m.sum():,} postings contain '{kw}'.")
        st.dataframe(rows, width="stretch", hide_index=True)
U.note("Correlation, not causation. Titles alone explain only part of pay variance (see R²); skills, experience level and project scope are not in the data.")
