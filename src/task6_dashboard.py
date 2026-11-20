"""Task 6 - monthly-updating dashboard. Re-reads every CSV in data/raw, so dropping in a new month's file and re-running refreshes everything."""
import json
from datetime import datetime, timezone
import numpy as np, pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from .common import load_clean, REPORTS, md_table
from .task4_country_rates import country_table

KPI_CSS = "body{font-family:system-ui,sans-serif;margin:0;padding:16px;background:#fafafa;color:#222}.k{display:flex;gap:12px;flex-wrap:wrap}.c{background:#fff;border:1px solid #e3e3e3;border-radius:8px;padding:12px 16px;min-width:150px}.c b{font-size:22px;display:block}.c small{color:#666}h1{font-size:20px}h2{font-size:16px;margin-top:28px}table{border-collapse:collapse;font-size:13px;display:block;overflow-x:auto}td,th{border:1px solid #ddd;padding:4px 8px}"


def month_summary(df):
    g = df.groupby("month")
    days = g.date.nunique()
    s = pd.DataFrame({
        "days_covered": days, "postings": g.size(), "postings_per_day": g.size() / days,
        "hourly_share_%": g.is_hourly.mean() * 100, "median_hourly": g.hourly_mid.median(), "median_fixed_budget": g.budget.median(),
        "remote_title_share_%": g.remote_mention.mean() * 100, "ai_share_%": g.category.apply(lambda x: (x == "AI / Machine Learning").mean() * 100),
        "us_share_%": g.country.apply(lambda x: (x == "United States").mean() * 100)})
    s["mom_postings_per_day_%"] = s.postings_per_day.pct_change() * 100
    return s.reset_index()


def build(df=None, out=REPORTS / "task6_dashboard.html"):
    df = df if df is not None else load_clean()
    ms = month_summary(df)
    daily = df.groupby("date").size()
    cat_m = df.groupby(["month", "category"]).size().unstack(fill_value=0)
    cat_share = cat_m.div(cat_m.sum(axis=1), axis=0) * 100
    ct, _, _ = country_table(df)

    fig = make_subplots(rows=3, cols=2, subplot_titles=("Daily postings", "Hourly vs fixed share (%) by week", "Category share by month (%)", "Median hourly rate by week (USD/h)", "Top countries by volume", "Remote-title share by week (%)"), vertical_spacing=.12)
    fig.add_trace(go.Scatter(x=daily.index, y=daily.values, name="postings"), 1, 1)
    wk = df.groupby("week").agg(h=("is_hourly", "mean"), r=("hourly_mid", "median"), rm=("remote_mention", "mean"), n=("title", "size"))
    wk = wk[wk.n > 20000]  # drop partial weeks
    fig.add_trace(go.Bar(x=wk.index, y=wk.h * 100, name="hourly %"), 1, 2)
    for c in cat_share.columns:
        if c != "Other":
            fig.add_trace(go.Bar(x=cat_share.index, y=cat_share[c], name=c), 2, 1)
    fig.add_trace(go.Scatter(x=wk.index, y=wk.r, mode="lines+markers", name="median hourly"), 2, 2)
    top = ct.sort_values("n_jobs", ascending=False).head(10)
    fig.add_trace(go.Bar(x=top.country, y=top.median_rate, name="median rate", text=top.n_jobs), 3, 1)
    fig.add_trace(go.Scatter(x=wk.index, y=wk.rm * 100, mode="lines+markers", name="remote %"), 3, 2)
    fig.update_layout(height=1100, barmode="stack", legend=dict(font=dict(size=9)), margin=dict(t=60))

    last = ms.iloc[-1]
    kpi = lambda lab, v: f'<div class="c"><b>{v}</b><small>{lab}</small></div>'
    html = f"""<!doctype html><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1"><title>Job Market Dashboard</title><style>{KPI_CSS}</style>
<h1>Upwork job market dashboard</h1><p>Generated {datetime.now(timezone.utc):%Y-%m-%d %H:%M} UTC &middot; data {df.date.min():%Y-%m-%d} to {df.date.max():%Y-%m-%d} &middot; latest month: {last.month:%B %Y} ({int(last.days_covered)} days)</p>
<div class=k>{kpi('postings (all data)', f'{len(df):,}')}{kpi('postings/day, latest month', f'{last.postings_per_day:,.0f}')}{kpi('hourly share', f'{last["hourly_share_%"]:.1f}%')}{kpi('median hourly rate', f'${last.median_hourly:.1f}')}{kpi('remote-titled', f'{last["remote_title_share_%"]:.1f}%')}{kpi('AI/ML share', f'{last["ai_share_%"]:.1f}%')}</div>
<h2>Month-by-month</h2>{ms.round(2).to_html(index=False)}
<p><small>Months with few covered days are partial; compare postings_per_day rather than totals.</small></p>
{fig.to_html(full_html=False, include_plotlyjs='cdn')}"""
    out.write_text(html, encoding="utf-8")
    ms.to_csv(REPORTS / "task6_monthly_summary.csv", index=False)
    return ms


if __name__ == "__main__":
    print(build())
