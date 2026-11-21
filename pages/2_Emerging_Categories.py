import plotly.express as px
import streamlit as st
import app_utils as U

U.setup("Task 2 - Emerging categories", "🌱", "Which categories and title keywords are gaining share of postings?")
cat = U.read_csv("task2_category_growth.csv")
kw = U.read_csv("task2_keyword_growth.csv")
st.markdown("Window A = **17 Feb - 1 Mar**, window B = **9 - 22 Mar** (each weekday appears exactly twice). Growth compares each category's *share* of postings, which removes overall volume swings.")

c = cat[cat.category != "Other"].sort_values("growth_%")
fig = px.bar(c, x="growth_%", y="category", orientation="h", color="emerging", color_discrete_map={True: "#2a9d8f", False: "#bbbbbb"}, title="Change in share of postings, window A to B (%)")
st.plotly_chart(fig, width="stretch")
em = cat[cat.emerging & (cat.category != "Other")].category.tolist()
st.success("Flagged emerging: " + (", ".join(em) if em else "none")) if em else st.info("No category passes the emerging test.")
st.dataframe(cat[["category", "share_A_%", "share_B_%", "growth_%", "slope_pp_per_week", "ab_p", "emerging"]], width="stretch", hide_index=True)

df = U.load_df()
w = df[(df.date >= "2024-02-19") & (df.date <= "2024-03-17")].groupby(["week", "category"]).size().reset_index(name="jobs")
w["share_%"] = w.jobs / w.groupby("week").jobs.transform("sum") * 100
pick = st.multiselect("Categories in the trend chart", sorted(w.category.unique()), default=["AI / Machine Learning", "Software / DevOps", "Web Development", "Writing / Content"])
st.plotly_chart(px.line(w[w.category.isin(pick)], x="week", y="share_%", color="category", markers=True, title="Weekly share of postings (complete weeks)"), width="stretch")

st.subheader("Title keywords")
mode = st.radio("Show", ["Growing", "Fading"], horizontal=True)
k = kw[kw["growth_%"] > 0].head(25) if mode == "Growing" else kw[kw["growth_%"] < 0].tail(25).iloc[::-1]
st.dataframe(k[["keyword", "jobs_A", "jobs_B", "per_1k_A", "per_1k_B", "growth_%", "p_adj"]], width="stretch", hide_index=True)
U.note("About 6 weeks of data: 'emerging' is short-term momentum, not a long-run trend. Keyword tests use a Bonferroni correction.")
