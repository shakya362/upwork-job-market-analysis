"""Task 1 - correlation between job-title keywords and offered pay."""
import json
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import plotly.express as px
from scipy import stats
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import RidgeCV
from sklearn.model_selection import cross_val_score, KFold
from .common import load_clean, REPORTS, md_table, write_report

MIN_DF = 100


def keyword_effects(df, target, label):
    d = df.dropna(subset=[target]).copy()
    y = np.log1p(d[target].values)
    cv = CountVectorizer(ngram_range=(1, 2), min_df=MIN_DF, binary=True, stop_words="english", token_pattern=r"(?u)\b[a-zA-Z][a-zA-Z0-9+#.]+\b")
    X = cv.fit_transform(d["title_clean"])
    vocab = np.array(cv.get_feature_names_out())
    rows = []
    Xc = X.tocsc()
    for j, kw in enumerate(vocab):
        m = Xc[:, j].toarray().ravel().astype(bool)
        a, b = d[target].values[m], d[target].values[~m]
        if len(a) < MIN_DF:
            continue
        u = stats.mannwhitneyu(a, b, alternative="two-sided")
        rb = stats.pearsonr(m.astype(float), y)[0]  # point-biserial vs log-pay
        rows.append((kw, m.sum(), np.median(a), np.median(b), np.mean(a) / np.mean(b), rb, u.pvalue))
    res = pd.DataFrame(rows, columns=["keyword", "n_jobs", "median_with", "median_without", "mean_ratio", "corr_log_pay", "p_value"])
    res["p_adj"] = np.minimum(res["p_value"] * len(res), 1.0)  # Bonferroni
    res["significant"] = res["p_adj"] < 0.01

    # Joint model: ridge on binary keywords -> log pay (controls for keyword overlap)
    ridge = RidgeCV(alphas=np.logspace(-1, 3, 12)).fit(X, y)
    r2 = cross_val_score(RidgeCV(alphas=[ridge.alpha_]), X, y, cv=KFold(5, shuffle=True, random_state=0), scoring="r2").mean()
    res["ridge_coef"] = res["keyword"].map(dict(zip(vocab, ridge.coef_)))
    res["target"] = label
    return res.sort_values("corr_log_pay", ascending=False), r2, len(d)


def plot_top(res, label, fname):
    top = pd.concat([res.head(12), res.tail(12)]).drop_duplicates("keyword").sort_values("corr_log_pay")
    fig, ax = plt.subplots(figsize=(7, 7))
    ax.barh(top["keyword"], top["corr_log_pay"], color=np.where(top["corr_log_pay"] > 0, "#2a9d8f", "#e76f51"))
    ax.set_title(f"Title keywords vs {label} (point-biserial r with log pay)")
    ax.axvline(0, color="k", lw=.5); plt.tight_layout(); plt.savefig(REPORTS / fname, dpi=130); plt.close()


def run(df=None):
    df = df if df is not None else load_clean()
    out = {}
    for target, label in [("hourly_mid", "hourly rate (USD/h)"), ("budget", "fixed-price budget (USD)")]:
        res, r2, n = keyword_effects(df, target, label)
        out[target] = (res, r2, n)
        res.to_csv(REPORTS / f"task1_{target}_keyword_effects.csv", index=False)
        plot_top(res, label, f"task1_{target}_keywords.png")
        sig = res[res.significant]
        fig = px.scatter(sig, x="corr_log_pay", y="median_with", size="n_jobs", hover_name="keyword", log_y=True, title=f"Keyword effect vs median {label}")
        fig.write_html(REPORTS / f"task1_{target}_scatter.html", include_plotlyjs="cdn")

    (REPORTS / "task1_meta.json").write_text(json.dumps({k: {"ridge_cv_r2": round(v[1], 4), "n_jobs": int(v[2])} for k, v in out.items()}))

    md = ["# Task 1 - Job-title keywords vs offered pay\n",
          f"Method: binary uni/bi-gram indicators (min {MIN_DF} postings) -> per-keyword Mann-Whitney U test (Bonferroni-adjusted) and point-biserial correlation with log pay, plus a joint Ridge regression (5-fold CV R2) so overlapping keywords are not double-counted.\n"]
    for target, label in [("hourly_mid", "Hourly rate"), ("budget", "Fixed-price budget")]:
        res, r2, n = out[target]
        cols = ["keyword", "n_jobs", "median_with", "median_without", "corr_log_pay", "p_adj"]
        sig = res[res.significant]
        md += [f"\n## {label}\n", f"Jobs analysed: {n:,}. Keywords tested: {len(res)}; significant (p_adj<0.01): {len(sig)}. Ridge CV R2 using title keywords alone: **{r2:.3f}**.\n",
               "\n**Keywords associated with HIGHER pay**\n\n", md_table(sig.head(12)[cols]),
               "\n\n**Keywords associated with LOWER pay**\n\n", md_table(sig.tail(12)[cols].iloc[::-1]), "\n"]
    md.append("\nInterpretation: correlation, not causation. Keywords are a weak-to-moderate predictor of pay; the R2 above says how much variance titles alone explain.")
    write_report("task1_keywords_vs_salary.md", "\n".join(md))
    return out


if __name__ == "__main__":
    run()
