"""Task 5 - content-based job recommendation engine over current postings.

Score = 0.70 * TF-IDF cosine(title, user query/skills)
      + 0.15 * category affinity (query's inferred category matches the job's)
      + 0.10 * recency (newer postings score higher)
      + 0.05 * pay fit (rate/budget at or above the user's minimum)
Hard filters: country, job type (hourly/fixed), minimum pay, remote-titled only.
"""
import joblib
import numpy as np, pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from .common import load_clean, categorize, MODELS

MODEL_PATH = MODELS / "recommender.joblib"
RECENT_DAYS = 14   # "current" postings = last N days of the data


class JobRecommender:
    def __init__(self):
        self.vec = None

    def fit(self, df: pd.DataFrame, recent_days: int = RECENT_DAYS):
        cutoff = df.date.max() - pd.Timedelta(days=recent_days - 1)
        d = df[df.date >= cutoff].drop_duplicates("title_clean").reset_index(drop=True)  # collapse repeated spam titles
        self.jobs = d[["title", "link", "published_date", "is_hourly", "hourly_low", "hourly_high", "hourly_mid", "budget", "country", "category", "remote_mention", "title_clean"]].copy()
        self.jobs["published_date"] = self.jobs["published_date"].astype(str)
        self.vec = TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True, stop_words="english")
        self.X = self.vec.fit_transform(self.jobs.title_clean)
        span = (d.published_date.max() - d.published_date.min()).total_seconds() or 1
        self.recency = ((d.published_date - d.published_date.min()).dt.total_seconds() / span).values
        return self

    def meta(self):
        j = self.jobs
        return {"n_jobs": len(j), "countries": sorted(j.country.unique().tolist()), "categories": sorted(j.category.unique().tolist()),
                "date_range": [j.published_date.min(), j.published_date.max()]}

    def recommend(self, query: str, top_n=10, country=None, job_type=None, min_rate=None, remote_only=False, category=None):
        j = self.jobs
        q = self.vec.transform([query.lower()])
        sim = linear_kernel(q, self.X).ravel()
        cat = category or categorize(query)
        cat_aff = (j.category.values == cat).astype(float)
        pay = np.where(j.is_hourly, j.hourly_mid, j.budget)
        pay_fit = np.ones(len(j)) if min_rate is None else np.where(np.isnan(pay), 0.3, (pay >= min_rate).astype(float))
        score = 0.70 * sim + 0.15 * cat_aff + 0.10 * self.recency + 0.05 * pay_fit

        mask = sim > 0 if query.strip() else np.ones(len(j), bool)
        if country:
            mask &= (j.country.str.lower() == country.lower()).values
        if job_type in ("hourly", "fixed"):
            mask &= (j.is_hourly.values == (job_type == "hourly"))
        if min_rate is not None:
            mask &= np.nan_to_num(pay, nan=-1) >= min_rate
        if remote_only:
            mask &= j.remote_mention.values
        idx = np.where(mask)[0]
        idx = idx[np.argsort(-score[idx])][:top_n]
        out = j.iloc[idx][["title", "link", "country", "is_hourly", "hourly_low", "hourly_high", "budget", "category", "published_date"]].copy()
        out["score"] = score[idx].round(4)
        out["match_reason"] = [f"title similarity {sim[i]:.2f}; category {j.category.iloc[i]}" for i in idx]
        return out.astype(object).where(out.notna(), None).to_dict("records")

    def save(self, path=MODEL_PATH):
        joblib.dump(self, path)

    @staticmethod
    def load(path=MODEL_PATH):
        return joblib.load(path)


def run(df=None):
    df = df if df is not None else load_clean()
    rec = JobRecommender().fit(df)
    rec.save()
    return rec


def evaluate(df, k=10, n_eval=500, seed=0):
    """Offline sanity check: query = a posting's own category-defining keywords; does the engine return same-category jobs?
    Reports precision@k of category agreement and catalogue coverage."""
    rec = JobRecommender().fit(df)
    rng = np.random.default_rng(seed)
    sample = rec.jobs[rec.jobs.category != "Other"].sample(n_eval, random_state=seed)
    hits, seen = [], set()
    for _, r in sample.iterrows():
        res = rec.recommend(r.title, top_n=k + 1)
        res = [x for x in res if x["title"] != r.title][:k]
        seen.update(x["link"] for x in res)
        hits.append(np.mean([x["category"] == r.category for x in res]) if res else 0)
    return {"precision_at_k_category": float(np.mean(hits)), "k": k, "coverage": len(seen) / len(rec.jobs), "n_eval": n_eval}


if __name__ == "__main__":
    d = load_clean()
    r = run(d)
    print(r.recommend("python data scientist machine learning", top_n=3))
    print(evaluate(d))
