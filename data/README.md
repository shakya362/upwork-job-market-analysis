# Data

- `raw/` - put the Upwork CSV(s) here (columns: title, link, published_date, is_hourly, hourly_low, hourly_high, budget, country). Not committed.
- `processed/` - compact parquet files the Streamlit app reads. **Committed.** Rebuild with `python scripts/build_processed.py`.
