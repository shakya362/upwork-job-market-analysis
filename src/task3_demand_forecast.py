"""Task 3 - forecast high-demand job roles from daily posting counts."""
import re
import numpy as np, pandas as pd
import plotly.graph_objects as go
import statsmodels.api as sm
from .common import load_clean, REPORTS, md_table, write_report

TRAIN_START, LAST_DAY, HOLDOUT_DAYS, HORIZON = "2024-02-16", "2024-03-22", 7, 14
ROLE_RX = re.compile(r"\b([a-z][a-z+#.]+(?: [a-z][a-z+#.]+)?) (developer|designer|editor|assistant|writer|manager|specialist|engineer|analyst|expert|marketer|artist|translator|consultant)\b")
STOP_FIRST = {"a", "an", "the", "and", "or", "for", "need", "needed", "with", "to", "of", "our", "my", "we", "looking", "hiring", "experienced", "expert", "skilled", "professional"}


def role_of(title):
    m = ROLE_RX.search(title)
    if not m:
        return None
    words = m.group(1).split()
    words = [w for w in words if w not in STOP_FIRST]
    return (" ".join(words) + " " + m.group(2)).strip() if words else m.group(2)


def build_series(df, n_roles=25):
    d = df[(df.date >= TRAIN_START) & (df.date <= LAST_DAY)].copy()
    d["role"] = d.title_clean.map(role_of)
    top_roles = d.role.value_counts().head(n_roles).index
    cats = d[d.category != "Other"].groupby(["date", "category"]).size().unstack(fill_value=0)
    roles = d[d.role.isin(top_roles)].groupby(["date", "role"]).size().unstack(fill_value=0)
    idx = pd.date_range(TRAIN_START, LAST_DAY)
    cats, roles = cats.reindex(idx, fill_value=0), roles.reindex(idx, fill_value=0)
    return cats, roles


def design(idx, t0=0):
    X = pd.get_dummies(idx.dayofweek).reindex(columns=range(7), fill_value=0).astype(float)
    X.index = idx
    X["t"] = (idx - idx[0]).days.values + t0
    return X.drop(columns=[0])  # Monday = baseline


def fit_predict(y, train_idx, pred_idx):
    X = sm.add_constant(design(train_idx))
    m = sm.OLS(np.log1p(y.loc[train_idx].values), X).fit()
    Xp = sm.add_constant(design(pred_idx, t0=(pred_idx[0] - train_idx[0]).days), has_constant="add")
    Xp["t"] = (pred_idx - train_idx[0]).days.values
    pr = m.get_prediction(Xp).summary_frame(alpha=0.2)
    return np.expm1(pr["mean"]).clip(lower=0), np.expm1(pr["obs_ci_lower"]).clip(lower=0), np.expm1(pr["obs_ci_upper"]).clip(lower=0), m


def evaluate(series: pd.DataFrame):
    idx = series.index
    tr, te = idx[:-HOLDOUT_DAYS], idx[-HOLDOUT_DAYS:]
    rows = []
    for c in series.columns:
        y = series[c]
        pred, *_ = fit_predict(y, tr, te)
        naive = y.shift(7).loc[te]  # seasonal naive baseline
        act = y.loc[te]
        mape = lambda p: np.mean(np.abs(act - p) / np.maximum(act, 1)) * 100
        rmse = lambda p: np.sqrt(np.mean((act - p) ** 2))
        rows.append((c, y.loc[tr].mean(), mape(pred), mape(naive), rmse(pred), rmse(naive)))
    r = pd.DataFrame(rows, columns=["series", "avg_daily_train", "MAPE_model_%", "MAPE_naive_%", "RMSE_model", "RMSE_naive"])
    r["beats_naive"] = r["RMSE_model"] < r["RMSE_naive"]
    return r


def forecast(series):
    idx = series.index
    fut = pd.date_range(idx[-1] + pd.Timedelta(days=1), periods=HORIZON)
    rows, curves = [], {}
    for c in series.columns:
        mean, lo, hi, m = fit_predict(series[c], idx, fut)
        last14 = series[c].iloc[-14:].sum()
        rows.append((c, last14, mean.sum(), (mean.sum() / max(last14, 1) - 1) * 100, m.params["t"] * 100 * 7))
        curves[c] = (mean, lo, hi)
    f = pd.DataFrame(rows, columns=["series", "jobs_last_14d", "forecast_next_14d", "change_%", "trend_%_per_week"])
    f["high_demand"] = f["forecast_next_14d"] >= f["forecast_next_14d"].quantile(0.75)
    return f.sort_values("forecast_next_14d", ascending=False), curves


def run(df=None):
    df = df if df is not None else load_clean()
    cats, roles = build_series(df)
    out = {}
    md = ["# Task 3 - High-demand job role prediction\n",
          f"Model: per-series OLS on log(1+daily postings) with day-of-week effects and a linear trend, trained on {TRAIN_START}..{LAST_DAY} "
          f"(the 15 Feb scrape gap is avoided by starting 16 Feb). Validation: last {HOLDOUT_DAYS} days held out vs a seasonal-naive baseline (same weekday last week). "
          f"Forecast horizon: {HORIZON} days with 80% prediction intervals.\n"]
    for name, s in (("categories", cats), ("roles", roles)):
        ev, (f, curves) = evaluate(s), forecast(s)
        ev.to_csv(REPORTS / f"task3_{name}_accuracy.csv", index=False)
        f.to_csv(REPORTS / f"task3_{name}_forecast.csv", index=False)
        med = ev[["MAPE_model_%", "MAPE_naive_%"]].median()
        md += [f"\n## {name.title()}\n", f"Median hold-out MAPE: model **{med['MAPE_model_%']:.1f}%** vs naive {med['MAPE_naive_%']:.1f}%. "
               f"Model beats naive RMSE on {ev.beats_naive.mean()*100:.0f}% of {len(ev)} series.\n\n", md_table(f.head(15)),
               "\n\nAccuracy per series:\n\n", md_table(ev.sort_values("avg_daily_train", ascending=False).head(15))]
        fig = go.Figure()
        for c in f.head(8).series:
            fig.add_trace(go.Scatter(x=s.index, y=s[c], name=c, mode="lines"))
            mean, lo, hi = curves[c]
            fig.add_trace(go.Scatter(x=mean.index, y=mean, name=f"{c} (forecast)", mode="lines", line=dict(dash="dash"), showlegend=False))
        fig.update_layout(title=f"Daily postings and {HORIZON}-day forecast - top {name}", yaxis_title="postings/day")
        fig.write_html(REPORTS / f"task3_{name}_demand.html", include_plotlyjs="cdn")
        out[name] = (ev, f)
    md.append("\nCaveat: ~5 weeks of history means the weekly pattern is learned from only ~5 cycles and the trend is short-term. Raw counts are also bounded by the feed's daily scrape volume, so treat ranks and relative growth as more reliable than absolute levels.")
    write_report("task3_demand_forecast.md", "\n".join(md))
    return out


if __name__ == "__main__":
    run()
