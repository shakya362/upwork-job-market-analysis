import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np, pandas as pd, pytest
from src.common import load_clean, categorize
from src.task5_recommender import JobRecommender
from src.task3_demand_forecast import role_of


@pytest.fixture(scope="module")
def df():
    return load_clean()


def test_cleaning(df):
    assert df.link.is_unique
    assert df.date.min() >= pd.Timestamp("2024-02-01")
    assert (df.hourly_low.dropna() >= 3).all() and (df.hourly_low <= df.hourly_high).where(df.hourly_low.notna() & df.hourly_high.notna(), True).all()
    assert df.country.notna().all()


def test_categorize():
    assert categorize("Python machine learning engineer") == "AI / Machine Learning"
    assert categorize("Shopify store developer") == "Web Development"
    assert categorize("zzz qqq") == "Other"


def test_role_of():
    assert role_of("need a shopify developer asap").endswith("developer")


def test_recommender_filters(df):
    rec = JobRecommender().fit(df)
    res = rec.recommend("video editor", top_n=5, job_type="hourly", country="United States", min_rate=15)
    assert 0 < len(res) <= 5
    assert all(r["is_hourly"] and r["country"] == "United States" for r in res)
    scores = [r["score"] for r in res]
    assert scores == sorted(scores, reverse=True)


def test_api():
    from app.app import app
    c = app.test_client()
    assert c.get("/api/health").json["status"] == "ok"
    assert c.post("/api/recommend", json={}).status_code == 400
    assert c.post("/api/recommend", json={"query": "x", "job_type": "bad"}).status_code == 400
    r = c.post("/api/recommend", json={"query": "logo designer", "top_n": 3})
    assert r.status_code == 200 and r.json["count"] <= 3


def test_remote_flag_ignores_virtual_assistant():
    from src.common import REMOTE_RX
    assert not REMOTE_RX.search("Virtual Assistant needed")
    assert REMOTE_RX.search("Remote Python developer")
    assert REMOTE_RX.search("Copywriter - work from home")
