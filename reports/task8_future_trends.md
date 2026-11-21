# Task 8 - Future job-market trends (scenario analysis)

Method: for each metric, an OLS trend with weekday effects is fitted on the clean window; the 28-day outlook comes in three scenarios. **Baseline** extends the fitted log-linear trend with damping (5% per day, so a short-term slope fades instead of compounding forever); **optimistic / cautious** use the upper/lower bound of the 80% confidence interval of the weekly trend slope. Values are the average of the final week of the horizon vs the last 14 days.


| metric | last_14d_avg | cautious | baseline | optimistic | baseline_change_% | trend_p | signal |
|---|---|---|---|---|---|---|---|
| Postings per day | 6,136.57 | 5,928.18 | 5,979.27 | 6,030.80 | -2.56 | 0.01 | significant |
| Hourly-contract share (%) | 56.59 | 55.08 | 55.32 | 55.56 | -2.24 | 0.00 | significant |
| Median hourly rate (USD/h) | 22.50 | 22.66 | 22.79 | 22.92 | 1.29 | 0.12 | flat / noisy |
| Median fixed budget (USD) | 93.93 | 89.46 | 91.10 | 92.77 | -3.01 | 0.17 | flat / noisy |
| Share: AI / Machine Learning (%) | 2.46 | 2.65 | 2.72 | 2.78 | 10.24 | 0.00 | significant |
| Share: Web Development (%) | 16.81 | 17.28 | 17.50 | 17.71 | 4.08 | 0.02 | significant |
| Share: Software / DevOps (%) | 4.37 | 4.68 | 4.76 | 4.83 | 8.88 | 0.00 | significant |
| Share: Writing / Content (%) | 4.43 | 3.47 | 3.57 | 3.67 | -19.47 | 0.00 | significant |
| Share: Translation (%) | 1.23 | 0.76 | 0.81 | 0.87 | -34.03 | 0.00 | significant |
| Share: remote-titled (%) | 0.57 | 0.56 | 0.59 | 0.62 | 3.24 | 0.46 | flat / noisy |


## Reading the results


- Statistically significant trends: Postings per day (-2.6%), Hourly-contract share (%) (-2.2%), Share: AI / Machine Learning (%) (+10.2%), Share: Web Development (%) (+4.1%), Share: Software / DevOps (%) (+8.9%), Share: Writing / Content (%) (-19.5%), Share: Translation (%) (-34.0%).

- Metrics marked 'flat / noisy' have no reliable direction; their three scenarios mostly bracket noise, so plan on the baseline staying near today's level.

- Outlook is deliberately short (4 weeks): the dataset covers about 5 weeks, so quarterly or yearly projections would be extrapolation without evidence. Re-running the pipeline as monthly files are added (see Task 6) lengthens the reliable horizon.