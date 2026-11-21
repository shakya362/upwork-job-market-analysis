"""Build the compact files the Streamlit app loads (run after adding new CSVs to data/raw/).

  data/processed/jobs_clean.parquet   all cleaned postings, no links (analytics pages)
  data/processed/jobs_recent.parquet  last 14 days with links (recommender)
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.common import load_clean, ROOT

OUT = ROOT / "data" / "processed"
OUT.mkdir(parents=True, exist_ok=True)

df = load_clean()
keep = [c for c in df.columns if c not in ("link", "title", "published_date")]
df[keep].to_parquet(OUT / "jobs_clean.parquet", compression="zstd", index=False)

recent = df[df.date >= df.date.max() - __import__("pandas").Timedelta(days=13)]
recent = recent.drop_duplicates("title_clean")   # the recommender collapses repeated titles anyway
recent.to_parquet(OUT / "jobs_recent.parquet", compression="zstd", index=False)
print({p.name: f"{p.stat().st_size / 1e6:.1f} MB" for p in OUT.glob("*.parquet")}, "| rows:", len(df), len(recent))
