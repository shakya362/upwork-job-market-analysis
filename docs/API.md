# Recommendation API

Base URL: `http://localhost:5000`

## `POST /api/recommend`  (also `GET` with query-string params)
| field | type | notes |
|---|---|---|
| `query` | string, **required** | skills / role / keywords |
| `top_n` | int | 1-50, default 10 |
| `country` | string | exact client country, e.g. `United States` |
| `job_type` | `hourly` \| `fixed` | |
| `min_rate` | number | min hourly midpoint (hourly jobs) or budget (fixed jobs) |
| `remote_only` | bool | only titles that mention remote/WFH/virtual |

```bash
curl -s localhost:5000/api/recommend -H 'Content-Type: application/json' \
  -d '{"query":"python data scientist","job_type":"hourly","min_rate":25,"top_n":3}'
```
Response: `{"query": "...", "count": 3, "results": [{"title","link","country","is_hourly","hourly_low","hourly_high","budget","category","published_date","score","match_reason"}]}`

Errors: `400 {"error": "..."}` for a missing query, a bad `job_type`, or non-numeric `top_n`/`min_rate`.

## `GET /api/meta` - index size, available countries/categories, date range
## `GET /api/health` - `{"status":"ok","jobs_indexed":N}`
## `GET /` UI  |  `GET /dashboard` Task 6 dashboard  |  `GET /reports/<file>` any generated report
