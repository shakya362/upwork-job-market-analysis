import plotly.express as px
import streamlit as st
import app_utils as U
from src.task6_dashboard import month_summary

U.setup("Task 6 - Monthly dashboard", "🗓️", "Month-by-month market KPIs. Re-run `scripts/build_processed.py` after adding a new month's CSV and this page updates.")
df = U.load_df()
f1, f2 = st.columns(2)
cats = f1.multiselect("Categories", sorted(df.category.unique()), placeholder="All categories")
ctry = f2.multiselect("Countries", df.country.value_counts().head(25).index.tolist(), placeholder="All countries")
if cats:
    df = df[df.category.isin(cats)]
if ctry:
    df = df[df.country.isin(ctry)]
if df.empty:
    st.warning("No postings match these filters."); st.stop()

ms = month_summary(df)
last = ms.iloc[-1]
prev = ms.iloc[-2] if len(ms) > 1 else None
d = lambda col: None if prev is None or prev[col] != prev[col] else f"{last[col] - prev[col]:+.1f}"
c = st.columns(5)
c[0].metric("Postings (filtered)", f"{len(df):,}")
c[1].metric(f"Postings/day, {last.month:%b}", f"{last.postings_per_day:,.0f}", d("postings_per_day"))
c[2].metric("Hourly share", f"{last['hourly_share_%']:.1f}%", d("hourly_share_%"))
c[3].metric("Median hourly rate", f"${last.median_hourly:.1f}", d("median_hourly"))
c[4].metric("AI/ML share", f"{last['ai_share_%']:.1f}%", d("ai_share_%"))
st.caption("Deltas compare the latest month with the previous one. February covers 17 days and March 24, so compare per-day figures, not totals.")

a, b = st.columns(2)
daily = df.groupby("date").size().reset_index(name="postings")
a.plotly_chart(px.line(daily, x="date", y="postings", title="Postings per day"), width="stretch")
wk = df.groupby("week").agg(n=("date", "size"), hourly=("is_hourly", "mean"), rate=("hourly_mid", "median")).reset_index()
wk = wk[wk.n >= wk.n.max() * 0.8]  # drop partial weeks
b.plotly_chart(px.line(wk, x="week", y="rate", markers=True, title="Median hourly rate by week (USD/h)"), width="stretch")
cm = df.groupby(["month", "category"]).size().reset_index(name="jobs")
cm["share_%"] = cm.jobs / cm.groupby("month").jobs.transform("sum") * 100
a.plotly_chart(px.bar(cm, x="month", y="share_%", color="category", title="Category mix by month (%)"), width="stretch")
top = df[df.country != "Unknown"].groupby("country").agg(postings=("date", "size"), median_hourly=("hourly_mid", "median")).nlargest(10, "postings").reset_index()
b.plotly_chart(px.bar(top, x="country", y="median_hourly", hover_data=["postings"], title="Top 10 countries by volume: median hourly rate"), width="stretch")
st.dataframe(ms.assign(month=ms.month.dt.strftime("%Y-%m")).round(2), width="stretch", hide_index=True)
