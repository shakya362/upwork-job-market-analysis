import plotly.graph_objects as go
import streamlit as st
import app_utils as U
from src import task8_future_trends as T8

U.setup("Task 8 - Future trends", "🔮", "Cautious, baseline and optimistic 4-week scenarios for key market metrics.")
df = U.load_df()


@st.cache_data(show_spinner="Fitting trends...")
def curves():
    out = {}
    for name, (y, _) in T8.metric_series(df).items():
        y = y.dropna()
        out[name] = (y, *T8.scenario(y, True))
    return out


C = curves()
tbl = U.read_csv("task8_scenarios.csv")
name = st.selectbox("Metric", list(C))
y, s, (fut, base, lo, hi) = C[name]
c = st.columns(4)
c[0].metric("Last 14 days", f"{s['now']:,.2f}")
c[1].metric("Cautious (week 4)", f"{s['cautious']:,.2f}")
c[2].metric("Baseline (week 4)", f"{s['base']:,.2f}", f"{(s['base'] / s['now'] - 1) * 100:+.1f}%")
c[3].metric("Optimistic (week 4)", f"{s['optimistic']:,.2f}")
(st.success if s["slope_p"] < 0.05 else st.info)(("Statistically significant trend" if s["slope_p"] < 0.05 else "No reliable trend: the scenarios mostly bracket noise") + f" (p = {s['slope_p']:.3f}).")
fig = go.Figure([go.Scatter(x=y.index, y=y, name="actual", line=dict(color="#555")),
                 go.Scatter(x=fut, y=base, name="baseline", line=dict(dash="dash", color="#1f77b4")),
                 go.Scatter(x=fut, y=hi, name="optimistic", line=dict(dash="dot", color="#2ca02c")),
                 go.Scatter(x=fut, y=lo, name="cautious", line=dict(dash="dot", color="#d62728"))])
fig.update_layout(margin=dict(t=10)); st.plotly_chart(fig, width="stretch")
st.subheader("All metrics")
st.dataframe(tbl, width="stretch", hide_index=True)
U.note("Log-linear trend with weekday effects and 5%/day trend damping. Cautious/optimistic use the 80% confidence bounds of the weekly slope. Horizon is kept to 4 weeks because only ~5 weeks of history exist.")
