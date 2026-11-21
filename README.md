# Job Market Analysis and Recommendation System

Built from the Next Hikes brief using `all_upwork_jobs_2024-02-07-2024-03-24.csv`
(244k Upwork postings: title, link, published_date, is_hourly, hourly_low/high, budget, country).

## Run
```bash
pip install -r requirements.txt
python -m src.run_all          # runs Tasks 1-8, writes reports/ and models/
python app/app.py              # UI at http://localhost:5000 (API docs: docs/API.md)
pytest -q tests
# or, with Docker:
docker compose up --build      # web on :5000, pipeline container re-runs monthly
```

## Streamlit app (streamlit.app)
```bash
pip install -r requirements.txt
streamlit run streamlit_app.py     # home page + 8 task pages from pages/
```
**Deploy on Streamlit Community Cloud**
1. Push the repo to GitHub. Commit `data/processed/*.parquet` and `reports/` (about 12 MB total); the raw CSV and `models/` are git-ignored and not needed.
2. Go to share.streamlit.io, choose **New app**, pick the repo and branch, and set **Main file path** to `streamlit_app.py`.
3. Under Advanced settings choose Python 3.12, then Deploy. The recommender index is built in about 2 seconds on first load.

**Refreshing with new data:** add the new CSV to `data/raw/`, then run `python -m src.run_all` (rebuilds `reports/` and `models/`) and `python scripts/build_processed.py` (rebuilds the app's parquet files), then commit and push. The app redeploys automatically.

## Task map
| Task | Code | Deliverable (in `reports/`) |
|---|---|---|
| EDA | `notebooks/01_eda.ipynb` | Annotated exploratory analysis; justifies every cleaning rule |
| 1 Title keywords vs pay | `src/task1_keywords_salary.py` | `task1_keywords_vs_salary.md`, CSVs, PNG + HTML charts |
| 2 Emerging categories | `src/task2_emerging.py` | `task2_emerging_categories.md`, `task2_category_trends.html` |
| 3 High-demand role forecast | `src/task3_demand_forecast.py` | `task3_demand_forecast.md` (hold-out MAPE/RMSE vs baseline), demand HTML |
| 4 Hourly rate by country | `src/task4_country_rates.py` | `task4_hourly_rate_map.html` (interactive), bar chart, report |
| 5 Recommendation engine | `src/task5_recommender.py`, `app/` | Flask API + UI, `docs/API.md` |
| 6 Monthly dashboard | `src/task6_dashboard.py`, `src/scheduler.py` | `task6_dashboard.html` (also served at `/dashboard`) |
| 7 Remote work trends | `src/task7_remote.py` | `task7_remote_trends.md`, forecast chart |
| 8 Future scenarios | `src/task8_future_trends.py` | `task8_future_trends.md`, `task8_scenarios.html` |

## Monthly updates (Task 6)
Drop each new month's CSV (same columns) into `data/raw/`. `load_clean()` concatenates all files and de-duplicates by link;
the `pipeline` container re-runs everything on the 1st of each month.

## Data caveats (read before presenting results)
- The file has no category, skills, description or location-requirement fields. **Categories are keyword rules on titles** (`CATEGORY_RULES` in `src/common.py`); ~23% fall in "Other".
- Dense data covers 13 Feb - 24 Mar 2024 (about 5.5 weeks). 283 stray rows from earlier dates are dropped; 15 Feb is a scrape gap and 24 Mar is partial, so models use 16 Feb - 22 Mar.
- Daily volume plateaus near 7k, which suggests the RSS feed was capped, so shares and growth rates are more trustworthy than absolute counts.
- Rates are advertised client ranges (midpoint), not earnings. Rates under $3 or over $300 and budgets under $5 or over $100k are treated as errors.
- Short history means "emerging" = short-term momentum, and forecasts are limited to 2-4 weeks. Task 8 uses damped trends for that reason.
- Task 7 "remote" = the title explicitly says remote / work-from-home (about 0.6% of postings; the word "virtual" is excluded because it mostly means "virtual assistant"). Every Upwork job is remote-style by nature, so this measures emphasis, not remote supply.
- Task 5 offline check: precision@10 of same-category matches is 0.93 (a sanity check, not a measure of user satisfaction; no click data exists).
- TensorFlow is in the brief but not used: with 36 daily points per series, OLS/Ridge/TF-IDF models are the appropriate size. Swap in an LSTM once several months of data exist.
