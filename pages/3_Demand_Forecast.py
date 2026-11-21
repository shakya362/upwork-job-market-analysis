import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import app_utils as U
from src import task3_demand_forecast as T3

U.setup("Task 3 - Demand forecast", "📈", "Forecast of daily postings for each category or role over the next 14 days.")
df = U.load_df()


@st.cache_data(show_spinner="Preparing series...")
def series():
    return T3.build_series(df)


cats, roles = series()
level = st.radio("Level", ["Categories", "Roles"], horizontal=True)
S = cats if level == "Categories" else roles
acc = U.read_csv(f"task3_{level.lower()}_accuracy.csv")
fc = U.read_csv(f"task3_{level.lower()}_forecast.csv")

med = acc[["MAPE_model_%", "MAPE_naive_%"]].median()
c = st.columns(3)
c[0].metric("Median hold-out MAPE (model)", f"{med['MAPE_model_%']:.1f}%")
c[1].metric("Median hold-out MAPE (naive)", f"{med['MAPE_naive_%']:.1f}%", help="Naive = same weekday last week.")
c[2].metric("Series beating naive (RMSE)", f"{acc.beats_naive.mean():.0%}")

name = st.selectbox("Series", fc.series.tolist())
y = S[name]
fut = pd.date_range(y.index[-1] + pd.Timedelta(days=1), periods=T3.HORIZON)
mean, lo, hi, _ = T3.fit_predict(y, y.index, fut)
fig = go.Figure([go.Scatter(x=y.index, y=y, name="actual"), go.Scatter(x=fut, y=mean, name="forecast", line=dict(dash="dash")),
                 go.Scatter(x=fut, y=hi, line=dict(width=0), showlegend=False), go.Scatter(x=fut, y=lo, fill="tonexty", line=dict(width=0), name="80% interval")])
fig.update_layout(yaxis_title="postings per day", margin=dict(t=10))
st.plotly_chart(fig, width="stretch")
row = fc[fc.series == name].iloc[0]
c = st.columns(3)
c[0].metric("Postings, last 14 days", f"{row.jobs_last_14d:,.0f}")
c[1].metric("Forecast, next 14 days", f"{row.forecast_next_14d:,.0f}", f"{row['change_%']:+.1f}%")
c[2].metric("High-demand (top quartile)?", "Yes" if row.high_demand else "No")

st.subheader(f"{level} ranked by forecast demand")
st.dataframe(fc, width="stretch", hide_index=True)
with st.expander("Hold-out accuracy per series"):
    st.dataframe(acc, width="stretch", hide_index=True)
U.note("Per-series OLS on log daily postings with weekday effects and a linear trend, trained on 16 Feb - 22 Mar; last 7 days held out. Role forecasts are noisier because counts are small.")
