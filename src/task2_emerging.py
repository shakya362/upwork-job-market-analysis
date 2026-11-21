"""Task 2 - emerging job categories (and emerging title keywords) from posting frequency."""
import numpy as np, pandas as pd
import plotly.express as px
import statsmodels.api as sm
from scipy import stats
from sklearn.feature_extraction.text import CountVectorizer
from .common import load_clean, REPORTS, md_table, write_report

# Two balanced 14-day windows (each weekday appears exactly twice), avoiding the 15 Feb scrape gap and partial last day.
A = ("2024-02-17", "2024-03-01")
B = ("2024-03-09", "2024-03-22")


def _slice(df, w):
    return df[(df.date >= w[0]) & (df.date <= w[1])]


def two_prop_p(ka, na, kb, nb):
    p = (ka + kb) / (na + nb)
    se = np.sqrt(p * (1 - p) * (1 / na + 1 / nb))
    z = (kb / nb - ka / na) / se if se > 0 else 0
    return 2 * (1 - stats.norm.cdf(abs(z)))


def category_growth(df):
    a, b = _slice(df, A), _slice(df, B)
    na, nb = len(a), len(b)
    ca, cb = a.category.value_counts(), b.category.value_counts()
    # daily-share trend (OLS with weekday dummies) over the whole clean span
    clean = df[(df.date >= "2024-02-16") & (df.date <= "2024-03-22")]
    share = clean.groupby(["date", "category"]).size().unstack(fill_value=0)
    share = share.div(share.sum(axis=1), axis=0)
    rows = []
    for c in share.columns:
        y = share[c].values
        X = pd.get_dummies(share.index.dayofweek, drop_first=True).astype(float)
        X.insert(0, "t", np.arange(len(y)))
        m = sm.OLS(y, sm.add_constant(X.values)).fit()
        rows.append((c, ca.get(c, 0), cb.get(c, 0), ca.get(c, 0) / na * 100, cb.get(c, 0) / nb * 100,
                     m.params[1] * 100 * 7, m.pvalues[1], two_prop_p(ca.get(c, 0), na, cb.get(c, 0), nb)))
    r = pd.DataFrame(rows, columns=["category", "jobs_A", "jobs_B", "share_A_%", "share_B_%", "slope_pp_per_week", "slope_p", "ab_p"])
    r["growth_%"] = (r["share_B_%"] / r["share_A_%"] - 1) * 100
    r["emerging"] = (r["growth_%"] > 5) & (r["ab_p"] < 0.01) & (r["slope_pp_per_week"] > 0)
    return r.sort_values("growth_%", ascending=False), share


def keyword_growth(df, min_total=200, top=30):
    a, b = _slice(df, A), _slice(df, B)
    cv = CountVectorizer(ngram_range=(1, 2), min_df=min_total, binary=True, stop_words="english",
                         token_pattern=r"(?u)\b[a-zA-Z][a-zA-Z0-9+#.]+\b")
    cv.fit(df["title_clean"])
    va = np.asarray(cv.transform(a.title_clean).sum(0)).ravel()
    vb = np.asarray(cv.transform(b.title_clean).sum(0)).ravel()
    na, nb = len(a), len(b)
    r = pd.DataFrame({"keyword": cv.get_feature_names_out(), "jobs_A": va, "jobs_B": vb})
    r = r[(r.jobs_A >= 30) & (r.jobs_B >= 30)].copy()
    r["per_1k_A"] = r.jobs_A / na * 1000
    r["per_1k_B"] = r.jobs_B / nb * 1000
    r["growth_%"] = (r.per_1k_B / r.per_1k_A - 1) * 100
    r["p"] = [two_prop_p(x, na, y, nb) for x, y in zip(r.jobs_A, r.jobs_B)]
    r["p_adj"] = np.minimum(r.p * len(r), 1)
    return r[(r.p_adj < 0.01)].sort_values("growth_%", ascending=False)


def run(df=None):
    df = df if df is not None else load_clean()
    cat, share = category_growth(df)
    kw = keyword_growth(df)
    cat.to_csv(REPORTS / "task2_category_growth.csv", index=False)
    kw.to_csv(REPORTS / "task2_keyword_growth.csv", index=False)

    wk = df[(df.date >= "2024-02-19") & (df.date <= "2024-03-17")].groupby(["week", "category"]).size().reset_index(name="jobs")
    wk["share_%"] = wk.jobs / wk.groupby("week").jobs.transform("sum") * 100
    px.line(wk[wk.category != "Other"], x="week", y="share_%", color="category", markers=True,
            title="Weekly share of postings by category (complete weeks)").write_html(REPORTS / "task2_category_trends.html", include_plotlyjs="cdn")

    kwc = ["keyword", "jobs_A", "jobs_B", "per_1k_A", "per_1k_B", "growth_%"]
    cols = ["category", "share_A_%", "share_B_%", "growth_%", "slope_pp_per_week", "ab_p"]
    emerging = cat[cat.emerging & (cat.category != "Other")]
    md = ["# Task 2 - Emerging job categories\n",
          f"Windows compared (14 days each, weekday-balanced): **A = {A[0]}..{A[1]}**, **B = {B[0]}..{B[1]}**. "
          "Share = category's fraction of all postings that day, which removes the effect of overall volume. "
          "Categories are keyword-derived from titles (the CSV has no category field).\n",
          "\n## Categories ranked by share growth\n\n", md_table(cat[cols]),
          "\n\n**Flagged emerging** (growth >5%, two-proportion p<0.01, positive weekday-adjusted trend): "
          + (", ".join(emerging.category) if len(emerging) else "none"),
          "\n\n## Emerging title keywords (Bonferroni p<0.01, growing)\n\n", md_table(kw[kw["growth_%"] > 0].head(25)[kwc]),
          "\n\n## Fading title keywords\n\n", md_table(kw[kw["growth_%"] < 0].tail(12).iloc[::-1][kwc]),
          "\n\nCaveat: the data spans about 6 weeks, so 'emerging' means short-term momentum, not a long-run trend."]
    write_report("task2_emerging_categories.md", "\n".join(md))
    return cat, kw


if __name__ == "__main__":
    run()
