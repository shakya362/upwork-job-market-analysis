"""Shared helpers for the Streamlit app (loaders are cached so pages stay fast)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd
import streamlit as st

PROC = ROOT / "data" / "processed"
REPORTS = ROOT / "reports"


def setup(title: str, icon: str = "📊", subtitle: str = ""):
    st.set_page_config(page_title=f"{title} | Job Market", page_icon=icon, layout="wide")
    st.title(f"{icon} {title}")
    if subtitle:
        st.caption(subtitle)


@st.cache_data(show_spinner="Loading data...")
def load_df() -> pd.DataFrame:
    return pd.read_parquet(PROC / "jobs_clean.parquet")


@st.cache_resource(show_spinner="Building recommendation index...")
def get_recommender():
    from src.task5_recommender import JobRecommender
    return JobRecommender().fit(pd.read_parquet(PROC / "jobs_recent.parquet"))


@st.cache_data
def read_csv(name: str) -> pd.DataFrame:
    return pd.read_csv(REPORTS / name)


def note(text: str):
    st.caption(f"ℹ️ {text}")
