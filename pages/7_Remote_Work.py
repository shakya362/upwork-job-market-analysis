import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from scipy import stats
import app_utils as U
from src import task7_remote as T7

U.setup("Task 7 - Remote work", "🏠", "How often do job titles stress remote work, and is it changing?")
st.info("Every Upwork job is remote by nature and the file has no location field. 'Remote' here means the **title says remote / work-from-home**. The word 'virtual' is excluded because most of those titles are *virtual assistants*.")
df = U.load_df()
d = df[(df.date >= T7.START) & (df.date <= T7.END)]

sig = {"remote_mention": "Remote / work-from-home", "onsite_mention": "On-site / hybrid", "longterm_mention": "Long-term / full-time / part-time"}
choice = st.selectbox("Signal", list(sig), format_func=sig.get)
s = T7.daily_share(df, choice)
m, fc = T7.trend_forecast(s)
c = st.columns(3)
c[0].metric("Postings with signal", f"{int(d[choice].sum()):,}")
c[1].metric("Average daily share", f"{s.mean():.2f}%")
c[2].metric("Trend per week", f"{m.params['t'] * 7:+.2f} pp", f"p = {m.pvalues['t']:.2f}", delta_color="off")
fig = go.Figure([go.Scatter(x=s.index, y=s, name="actual"), go.Scatter(x=fc.index, y=fc["mean"], name="forecast", line=dict(dash="dash")),
                 go.Scatter(x=fc.index, y=fc["obs_ci_upper"], line=dict(width=0), showlegend=False),
                 go.Scatter(x=fc.index, y=fc["obs_ci_lower"], fill="tonexty", line=dict(width=0), name="80% interval")])
fig.update_layout(yaxis_title="% of postings", margin=dict(t=10)); st.plotly_chart(fig, width="stretch")

a, b = st.columns(2)
cat = d.groupby("category").agg(jobs=("date", "size"), share=(choice, "mean")).assign(share=lambda x: x.share * 100).sort_values("share", ascending=False)
a.subheader("By category"); a.dataframe(cat.round(2), width="stretch")
ct = d[d.country != "Unknown"].groupby("country").agg(jobs=("date", "size"), share=(choice, "mean")).assign(share=lambda x: x.share * 100)
b.subheader("By country (>= 500 postings)"); b.dataframe(ct[ct.jobs >= 500].sort_values("share", ascending=False).head(15).round(2), width="stretch")

st.subheader("Does remote wording go with different pay or contract type?")
r, o = d[d.remote_mention], d[~d.remote_mention]
ha, hb = r.hourly_mid.dropna(), o.hourly_mid.dropna()
ba, bb = r.budget.dropna(), o.budget.dropna()
chi = stats.chi2_contingency(pd.crosstab(d.remote_mention, d.is_hourly))[1]
st.dataframe([
    {"metric": "Median hourly rate", "remote-titled": ha.median(), "other": hb.median(), "p-value": stats.mannwhitneyu(ha, hb).pvalue},
    {"metric": "Median fixed budget", "remote-titled": ba.median(), "other": bb.median(), "p-value": stats.mannwhitneyu(ba, bb).pvalue},
    {"metric": "Hourly share of contracts (%)", "remote-titled": r.is_hourly.mean() * 100, "other": o.is_hourly.mean() * 100, "p-value": chi}],
    width="stretch", hide_index=True)
