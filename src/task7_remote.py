"""Task 7 - remote-work landscape."""
import numpy as np, pandas as pd
import plotly.express as px
import statsmodels.api as sm
from scipy import stats
from .common import load_clean, REPORTS, md_table, write_report
from .task3_demand_forecast import design

START, END, HORIZON = "2024-02-16", "2024-03-22", 28


def daily_share(df, col):
    d = df[(df.date >= START) & (df.date <= END)]
    return d.groupby("date")[col].mean() * 100


def trend_forecast(s):
    X = sm.add_constant(design(s.index))
    m = sm.OLS(s.values, X).fit()
    fut = pd.date_range(s.index[-1] + pd.Timedelta(days=1), periods=HORIZON)
    Xf = sm.add_constant(design(fut), has_constant="add")
    Xf["t"] = (fut - s.index[0]).days.values
    pr = m.get_prediction(Xf).summary_frame(alpha=0.2)
    return m, pr.set_index(fut)


def run(df=None):
    df = df if df is not None else load_clean()
    d = df[(df.date >= START) & (df.date <= END)]
    sig = {"remote_mention": "Remote / work-from-home in title", "onsite_mention": "On-site / hybrid in title", "longterm_mention": "Long-term / full-time / part-time in title"}
    res, series = [], {}
    for col, label in sig.items():
        s = daily_share(df, col); series[col] = s
        m, fc = trend_forecast(s)
        res.append((label, d[col].sum(), s.mean(), m.params["t"] * 7, m.pvalues["t"], fc["mean"].iloc[-1], fc["obs_ci_lower"].iloc[-1], fc["obs_ci_upper"].iloc[-1]))
    r = pd.DataFrame(res, columns=["signal", "postings", "avg_daily_share_%", "trend_pp_per_week", "trend_p", "forecast_share_%_in_28d", "lo80", "hi80"])
    r.to_csv(REPORTS / "task7_remote_signals.csv", index=False)

    wk = d.groupby("week").agg(remote_share=("remote_mention", "mean"), hourly_share=("is_hourly", "mean"), jobs=("title", "size")).mul([100, 100, 1]).reset_index()
    wk = wk[(wk.week >= "2024-02-19") & (wk.week <= "2024-03-11")]  # complete Mon-Sun weeks
    px.line(wk.melt("week", ["remote_share", "hourly_share"]), x="week", y="value", color="variable", markers=True, title="Weekly remote-mention share and hourly-contract share (%)").write_html(REPORTS / "task7_remote_weekly.html", include_plotlyjs="cdn")
    s = series["remote_mention"]; _, fc = trend_forecast(s)
    import plotly.graph_objects as go
    f = go.Figure([go.Scatter(x=s.index, y=s, name="actual"), go.Scatter(x=fc.index, y=fc["mean"], name="forecast", line=dict(dash="dash")),
                   go.Scatter(x=fc.index, y=fc["obs_ci_upper"], line=dict(width=0), showlegend=False), go.Scatter(x=fc.index, y=fc["obs_ci_lower"], fill="tonexty", line=dict(width=0), name="80% interval")])
    f.update_layout(title="Share of postings mentioning remote work: actual and 28-day forecast (%)"); f.write_html(REPORTS / "task7_remote_forecast.html", include_plotlyjs="cdn")

    cat = d.groupby("category").agg(jobs=("title", "size"), remote_share=("remote_mention", "mean")).reset_index(); cat["remote_share"] *= 100
    ctry = d[d.country != "Unknown"].groupby("country").agg(jobs=("title", "size"), remote_share=("remote_mention", "mean")).reset_index(); ctry["remote_share"] *= 100
    ctry = ctry[ctry.jobs >= 500].sort_values("remote_share", ascending=False)
    a, b = d[d.remote_mention].hourly_mid.dropna(), d[~d.remote_mention].hourly_mid.dropna()
    ba, bb = d[d.remote_mention].budget.dropna(), d[~d.remote_mention].budget.dropna()
    p_h, p_b = stats.mannwhitneyu(a, b).pvalue, stats.mannwhitneyu(ba, bb).pvalue
    ct = pd.crosstab(d.remote_mention, d.is_hourly); chi = stats.chi2_contingency(ct)

    md = ["# Task 7 - Remote work landscape\n",
          "Important limitation: every Upwork posting is remote-by-default, and the file has no location-requirement, skills or description field. "
          "'Remote' here means the **title explicitly says** remote / work-from-home (the word 'virtual' is excluded because it mostly means 'virtual assistant') (and on-site/hybrid wording as a counter-signal). Read it as emphasis, not total remote supply. A few matches are technical false positives (e.g. 'remote desktop', 'remote config').\n",
          f"\nWindow: {START}..{END}. Trend = OLS on daily share with weekday effects; 28-day forecast with 80% interval.\n\n", md_table(r),
          "\n\n## Remote-mention share by category\n\n", md_table(cat.sort_values("remote_share", ascending=False)),
          "\n\n## Remote-mention share by country (>=500 postings)\n\n", md_table(ctry.head(10)),
          f"\n\n## Does 'remote' wording go with different pay or contract type?\n\n- Median hourly rate, remote-titled vs other: **{a.median():.1f}** vs **{b.median():.1f}** (Mann-Whitney p={p_h:.2g}, n={len(a):,} / {len(b):,})\n"
          f"- Median fixed budget, remote-titled vs other: **{ba.median():.0f}** vs **{bb.median():.0f}** (p={p_b:.2g})\n"
          f"- Hourly share of contracts: remote-titled **{d[d.remote_mention].is_hourly.mean()*100:.1f}%** vs other **{d[~d.remote_mention].is_hourly.mean()*100:.1f}%** (chi-square p={chi[1]:.2g})\n"]
    write_report("task7_remote_trends.md", "\n".join(md))
    return r


if __name__ == "__main__":
    run()
