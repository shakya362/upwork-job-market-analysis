"""Task 8 - future job-market scenarios (baseline / optimistic / cautious) over the next 4 weeks."""
import numpy as np, pandas as pd
import statsmodels.api as sm
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from .common import load_clean, REPORTS, md_table, write_report
from .task3_demand_forecast import design

START, END, HORIZON, PHI = "2024-02-16", "2024-03-22", 28, 0.95  # PHI: trend damping per day


def metric_series(df):
    d = df[(df.date >= START) & (df.date <= END)]
    g = d.groupby("date")
    m = {
        "Postings per day": (g.size().astype(float), True),
        "Hourly-contract share (%)": (g.is_hourly.mean() * 100, False),
        "Median hourly rate (USD/h)": (g.hourly_mid.median(), False),
        "Median fixed budget (USD)": (g.budget.median(), False),
    }
    for c in ["AI / Machine Learning", "Web Development", "Software / DevOps", "Writing / Content", "Translation"]:
        m[f"Share: {c} (%)"] = (g.category.apply(lambda s, c=c: (s == c).mean() * 100), False)
    m["Share: remote-titled (%)"] = (g.remote_mention.mean() * 100, False)
    return m


def scenario(y, log):
    idx = y.index
    X = sm.add_constant(design(idx))
    yy = np.log(y.values) if log else y.values
    mod = sm.OLS(yy, X).fit()
    fut = pd.date_range(idx[-1] + pd.Timedelta(days=1), periods=HORIZON)
    dt = np.cumsum(PHI ** np.arange(1, HORIZON + 1))          # damped trend steps
    Xf = sm.add_constant(design(fut), has_constant="add"); Xf["t"] = (idx[-1] - idx[0]).days + dt
    base = mod.predict(Xf)
    lo, hi = mod.conf_int(alpha=0.2).loc["t"]            # 80% interval for the slope
    cautious, optimistic = base + (lo - mod.params["t"]) * dt, base + (hi - mod.params["t"]) * dt
    f = (lambda v: np.exp(v)) if log else (lambda v: v)
    wkavg = lambda v: float(np.mean(f(v)[-7:]))
    last = float(y.iloc[-14:].mean())
    return dict(now=last, base=wkavg(base), cautious=wkavg(cautious), optimistic=wkavg(optimistic),
                slope_p=mod.pvalues["t"], r2=mod.rsquared), (fut, f(base), f(cautious), f(optimistic))


def run(df=None):
    df = df if df is not None else load_clean()
    rows, curves = [], {}
    for name, (y, log) in metric_series(df).items():
        y = y.dropna()
        s, c = scenario(y, True)
        curves[name] = (y, c)
        chg = (s["base"] / s["now"] - 1) * 100
        rows.append((name, s["now"], s["cautious"], s["base"], s["optimistic"], chg, s["slope_p"], "significant" if s["slope_p"] < 0.05 else "flat / noisy"))
    r = pd.DataFrame(rows, columns=["metric", "last_14d_avg", "cautious", "baseline", "optimistic", "baseline_change_%", "trend_p", "signal"])
    r.to_csv(REPORTS / "task8_scenarios.csv", index=False)

    names = list(curves)
    fig = make_subplots(rows=(len(names) + 1) // 2, cols=2, subplot_titles=names)
    for i, n in enumerate(names):
        y, (fut, b, lo, hi) = curves[n]; rr, cc = i // 2 + 1, i % 2 + 1
        fig.add_trace(go.Scatter(x=y.index, y=y, line=dict(color="#555"), showlegend=False), rr, cc)
        for v, nm, col in ((b, "baseline", "#1f77b4"), (hi, "optimistic", "#2ca02c"), (lo, "cautious", "#d62728")):
            fig.add_trace(go.Scatter(x=fut, y=v, name=nm, line=dict(color=col, dash="dash"), showlegend=(i == 0)), rr, cc)
    fig.update_layout(height=260 * ((len(names) + 1) // 2), title="Scenarios: next 28 days (cautious/baseline/optimistic = 80% slope bounds)")
    fig.write_html(REPORTS / "task8_scenarios.html", include_plotlyjs="cdn")

    sig = r[r.signal == "significant"]
    md = ["# Task 8 - Future job-market trends (scenario analysis)\n",
          "Method: for each metric, an OLS trend with weekday effects is fitted on the clean window; the 28-day outlook comes in three scenarios. "
          "**Baseline** extends the fitted log-linear trend with damping (5% per day, so a short-term slope fades instead of compounding forever); **optimistic / cautious** use the upper/lower bound of the 80% confidence interval of the weekly trend slope. "
          "Values are the average of the final week of the horizon vs the last 14 days.\n\n", md_table(r),
          "\n\n## Reading the results\n\n",
          "- Statistically significant trends: " + (", ".join(f"{a} ({b:+.1f}%)" for a, b in zip(sig.metric, sig["baseline_change_%"])) if len(sig) else "none") + ".\n",
          "- Metrics marked 'flat / noisy' have no reliable direction; their three scenarios mostly bracket noise, so plan on the baseline staying near today's level.\n",
          "- Outlook is deliberately short (4 weeks): the dataset covers about 5 weeks, so quarterly or yearly projections would be extrapolation without evidence. "
          "Re-running the pipeline as monthly files are added (see Task 6) lengthens the reliable horizon."]
    write_report("task8_future_trends.md", "\n".join(md))
    return r


if __name__ == "__main__":
    run()
