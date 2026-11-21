"""Task 4 - average hourly rates by country (interactive map + chart)."""
import numpy as np, pandas as pd
import plotly.express as px
from scipy import stats
from .common import load_clean, REPORTS, md_table, write_report

MIN_JOBS = 30


def boot_ci(x, n=300, seed=0):
    rng = np.random.default_rng(seed)
    meds = [np.median(rng.choice(x, len(x))) for _ in range(n)]
    return np.percentile(meds, [2.5, 97.5])


def country_table(df):
    h = df[(df.is_hourly) & df.hourly_mid.notna() & (df.country != "Unknown")]
    g = h.groupby("country")["hourly_mid"]
    t = g.agg(n_jobs="size", mean_rate="mean", median_rate="median", p25=lambda s: s.quantile(.25), p75=lambda s: s.quantile(.75)).reset_index()
    t["avg_low"] = t.country.map(h.groupby("country").hourly_low.mean())
    t["avg_high"] = t.country.map(h.groupby("country").hourly_high.mean())
    t = t[t.n_jobs >= MIN_JOBS].copy()
    ci = {c: boot_ci(h.loc[h.country == c, "hourly_mid"].values) for c in t.country}
    t["median_ci_low"] = t.country.map(lambda c: ci[c][0])
    t["median_ci_high"] = t.country.map(lambda c: ci[c][1])
    fixed = df[~df.is_hourly & df.budget.notna()].groupby("country").budget.median()
    t["median_fixed_budget"] = t.country.map(fixed)
    kw = stats.kruskal(*[h.loc[h.country == c, "hourly_mid"].values for c in t.country])
    return t.sort_values("median_rate", ascending=False), kw, len(h)


def run(df=None):
    df = df if df is not None else load_clean()
    t, kw, n = country_table(df)
    t.to_csv(REPORTS / "task4_country_hourly_rates.csv", index=False)
    px.choropleth(t, locations="country", locationmode="country names", color="median_rate", hover_name="country",
                  hover_data={"n_jobs": True, "mean_rate": ":.1f", "median_ci_low": ":.1f", "median_ci_high": ":.1f"},
                  color_continuous_scale="Viridis", title=f"Median advertised hourly rate by client country (USD/h, n>={MIN_JOBS})"
                  ).write_html(REPORTS / "task4_hourly_rate_map.html", include_plotlyjs="cdn")
    top = pd.concat([t.head(15), t.tail(15)]).drop_duplicates("country")
    px.bar(top.sort_values("median_rate"), x="median_rate", y="country", orientation="h", error_x=top.sort_values("median_rate").median_ci_high - top.sort_values("median_rate").median_rate,
           error_x_minus=top.sort_values("median_rate").median_rate - top.sort_values("median_rate").median_ci_low, height=700,
           title="Highest and lowest median hourly rates (95% bootstrap CI)").write_html(REPORTS / "task4_hourly_rate_bar.html", include_plotlyjs="cdn")
    cols = ["country", "n_jobs", "median_rate", "mean_rate", "median_ci_low", "median_ci_high"]
    md = ["# Task 4 - Hourly rates by country\n",
          f"Basis: {n:,} hourly postings with a stated rate; rate = midpoint of the advertised low/high range (USD/h); country = client country of the posting. "
          f"{len(t)} countries with >= {MIN_JOBS} postings. Kruskal-Wallis across countries: H={kw.statistic:.0f}, p={kw.pvalue:.2g}.\n",
          "\n## Highest median rates\n\n", md_table(t.head(12)[cols]), "\n\n## Lowest median rates\n\n", md_table(t.tail(12)[cols].iloc[::-1]),
          "\n\n## Most active markets\n\n", md_table(t.sort_values("n_jobs", ascending=False).head(10)[cols]),
          "\n\nNote: these are rates clients advertise, not rates freelancers earn, and the country is the client's, not the freelancer's."]
    write_report("task4_country_hourly_rates.md", "\n".join(md))
    return t


if __name__ == "__main__":
    run()
