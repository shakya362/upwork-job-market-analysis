# Task 7 - Remote work landscape

Important limitation: every Upwork posting is remote-by-default, and the file has no location-requirement, skills or description field. 'Remote' here means the **title explicitly says** remote / work-from-home (the word 'virtual' is excluded because it mostly means 'virtual assistant') (and on-site/hybrid wording as a counter-signal). Read it as emphasis, not total remote supply. A few matches are technical false positives (e.g. 'remote desktop', 'remote config').


Window: 2024-02-16..2024-03-22. Trend = OLS on daily share with weekday effects; 28-day forecast with 80% interval.


| signal | postings | avg_daily_share_% | trend_pp_per_week | trend_p | forecast_share_%_in_28d | lo80 | hi80 |
|---|---|---|---|---|---|---|---|
| Remote / work-from-home in title | 1262 | 0.55 | 0.01 | 0.42 | 0.60 | 0.43 | 0.78 |
| On-site / hybrid in title | 241 | 0.11 | -0.00 | 0.99 | 0.12 | 0.04 | 0.21 |
| Long-term / full-time / part-time in title | 4170 | 1.84 | 0.00 | 0.94 | 1.73 | 1.38 | 2.09 |


## Remote-mention share by category


| category | jobs | remote_share |
|---|---|---|
| Customer Support | 2675 | 3.25 |
| Sales / Lead Gen | 8287 | 2.15 |
| Admin / Virtual Assistant | 9195 | 1.91 |
| Data / Analytics | 10414 | 0.84 |
| Other | 51211 | 0.59 |
| Finance / Legal | 3672 | 0.57 |
| Writing / Content | 10959 | 0.51 |
| AI / Machine Learning | 5211 | 0.50 |
| Software / DevOps | 9388 | 0.47 |
| Mobile Apps | 6274 | 0.45 |
| SEO / Marketing | 20336 | 0.41 |
| Video / Audio | 19659 | 0.24 |
| Web Development | 37353 | 0.22 |
| Translation | 3312 | 0.21 |
| Engineering / Other Tech | 1941 | 0.21 |
| Design / Creative | 25102 | 0.13 |


## Remote-mention share by country (>=500 postings)


| country | jobs | remote_share |
|---|---|---|
| Japan | 689 | 2.03 |
| Vietnam | 538 | 1.67 |
| Philippines | 2289 | 0.92 |
| United States | 91678 | 0.87 |
| Kenya | 759 | 0.66 |
| Ireland | 1080 | 0.65 |
| Singapore | 2326 | 0.56 |
| Italy | 1648 | 0.55 |
| South Africa | 950 | 0.53 |
| Nigeria | 968 | 0.52 |


## Does 'remote' wording go with different pay or contract type?

- Median hourly rate, remote-titled vs other: **25.0** vs **22.5** (Mann-Whitney p=0.054, n=750 / 93,369)
- Median fixed budget, remote-titled vs other: **160** vs **100** (p=0.00022)
- Hourly share of contracts: remote-titled **75.0%** vs other **57.4%** (chi-square p=5.1e-36)
