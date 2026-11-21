import plotly.express as px
import streamlit as st
import app_utils as U

U.setup("Task 4 - Hourly rates by country", "🌍", "Advertised hourly rates by client country (midpoint of the stated range, USD/h).")
t = U.read_csv("task4_country_hourly_rates.csv")
c1, c2 = st.columns(2)
min_n = c1.slider("Minimum hourly postings per country", 30, 2000, 100, step=10)
metric = c2.radio("Colour by", ["median_rate", "mean_rate"], horizontal=True)
d = t[t.n_jobs >= min_n]
st.caption(f"{len(d)} countries shown.")

st.plotly_chart(px.choropleth(d, locations="country", locationmode="country names", color=metric, hover_name="country",
                              hover_data={"n_jobs": True, "median_ci_low": ":.1f", "median_ci_high": ":.1f"}, color_continuous_scale="Viridis"), width="stretch")
st.subheader("Compare countries")
default = [x for x in ["United States", "United Kingdom", "India", "Pakistan", "Australia", "Canada"] if x in d.country.values]
pick = st.multiselect("Countries", d.country.tolist(), default=default)
if pick:
    p = d[d.country.isin(pick)].sort_values("median_rate")
    fig = px.bar(p, x="median_rate", y="country", orientation="h", error_x=p.median_ci_high - p.median_rate, error_x_minus=p.median_rate - p.median_ci_low)
    fig.update_layout(xaxis_title="median USD/h (95% bootstrap CI)", margin=dict(t=10))
    st.plotly_chart(fig, width="stretch")
st.dataframe(d[["country", "n_jobs", "median_rate", "mean_rate", "p25", "p75", "median_ci_low", "median_ci_high", "median_fixed_budget"]], width="stretch", hide_index=True)
U.note("Country is the client's country. Rates are advertised, not earned, and only hourly postings that state a rate are included.")
