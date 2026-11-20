# Task 3 - High-demand job role prediction

Model: per-series OLS on log(1+daily postings) with day-of-week effects and a linear trend, trained on 2024-02-16..2024-03-22 (the 15 Feb scrape gap is avoided by starting 16 Feb). Validation: last 7 days held out vs a seasonal-naive baseline (same weekday last week). Forecast horizon: 14 days with 80% prediction intervals.


## Categories

Median hold-out MAPE: model **8.3%** vs naive 8.9%. Model beats naive RMSE on 87% of 15 series.


| series | jobs_last_14d | forecast_next_14d | change_% | trend_%_per_week | high_demand |
|---|---|---|---|---|---|
| Web Development | 14437 | 14,628.07 | 1.32 | 0.24 | True |
| Design / Creative | 9722 | 9,755.97 | 0.35 | 0.03 | True |
| SEO / Marketing | 7855 | 7,811.52 | -0.55 | -0.26 | True |
| Video / Audio | 7565 | 7,503.99 | -0.81 | -0.47 | True |
| Software / DevOps | 3759 | 3,918.52 | 4.24 | 2.05 | False |
| Admin / Virtual Assistant | 3507 | 3,405.48 | -2.89 | -1.24 | False |
| Data / Analytics | 3798 | 3,351.36 | -11.76 | -5.07 | False |
| Sales / Lead Gen | 3264 | 3,296.74 | 1.00 | 0.73 | False |
| Writing / Content | 3827 | 3,198.31 | -16.43 | -7.62 | False |
| Mobile Apps | 2389 | 2,358.05 | -1.30 | -0.86 | False |
| AI / Machine Learning | 2095 | 2,196.41 | 4.84 | 2.36 | False |
| Finance / Legal | 1387 | 1,449.02 | 4.47 | 0.60 | False |
| Customer Support | 1042 | 1,046.92 | 0.47 | 0.40 | False |
| Translation | 1085 | 775.45 | -28.53 | -12.98 | False |
| Engineering / Other Tech | 734 | 727.55 | -0.88 | -0.66 | False |


Accuracy per series:


| series | avg_daily_train | MAPE_model_% | MAPE_naive_% | RMSE_model | RMSE_naive | beats_naive |
|---|---|---|---|---|---|---|
| Web Development | 1,036.31 | 3.81 | 3.69 | 41.52 | 46.52 | True |
| Design / Creative | 700.72 | 5.63 | 6.23 | 44.31 | 50.46 | True |
| SEO / Marketing | 570.03 | 9.35 | 8.89 | 64.63 | 59.02 | False |
| Video / Audio | 550.07 | 5.56 | 5.87 | 33.19 | 39.49 | True |
| Writing / Content | 314.38 | 6.59 | 9.70 | 21.53 | 30.91 | True |
| Data / Analytics | 294.34 | 8.38 | 11.09 | 34.38 | 36.02 | True |
| Software / DevOps | 257.97 | 4.67 | 5.08 | 12.83 | 16.11 | True |
| Admin / Virtual Assistant | 256.79 | 5.13 | 5.76 | 20.97 | 16.39 | False |
| Sales / Lead Gen | 228.59 | 10.32 | 8.71 | 28.33 | 28.41 | True |
| Mobile Apps | 176.00 | 8.39 | 10.07 | 18.47 | 18.59 | True |
| AI / Machine Learning | 144.31 | 9.52 | 8.63 | 14.81 | 16.13 | True |
| Finance / Legal | 101.97 | 9.64 | 9.84 | 12.19 | 12.38 | True |
| Translation | 97.31 | 8.26 | 19.49 | 8.91 | 20.71 | True |
| Customer Support | 73.62 | 8.04 | 15.28 | 14.20 | 19.89 | True |
| Engineering / Other Tech | 54.28 | 13.57 | 25.77 | 8.92 | 16.09 | True |

## Roles

Median hold-out MAPE: model **33.6%** vs naive 36.4%. Model beats naive RMSE on 76% of 25 series.


| series | jobs_last_14d | forecast_next_14d | change_% | trend_%_per_week | high_demand |
|---|---|---|---|---|---|
| video editor | 1088 | 1,091.60 | 0.33 | 0.82 | True |
| graphic designer | 1039 | 1,057.44 | 1.78 | 1.03 | True |
| virtual assistant | 717 | 629.98 | -12.14 | -5.22 | True |
| social media manager | 513 | 500.72 | -2.39 | -1.32 | True |
| full stack developer | 341 | 345.24 | 1.24 | 1.89 | True |
| ui ux designer | 253 | 282.62 | 11.71 | 3.64 | True |
| wordpress developer | 241 | 254.18 | 5.47 | 3.15 | True |
| web developer | 231 | 231.91 | 0.39 | -0.53 | False |
| youtube video editor | 222 | 224.88 | 1.30 | 0.38 | False |
| script writer | 170 | 196.75 | 15.74 | 8.92 | False |
| expert | 142 | 154.62 | 8.88 | 2.52 | False |
| shopify developer | 144 | 154.08 | 7.00 | 3.60 | False |
| logo designer | 169 | 152.98 | -9.48 | -1.45 | False |
| web designer | 159 | 152.84 | -3.88 | 1.30 | False |
| seo expert | 155 | 137.25 | -11.45 | -1.98 | False |


Accuracy per series:


| series | avg_daily_train | MAPE_model_% | MAPE_naive_% | RMSE_model | RMSE_naive | beats_naive |
|---|---|---|---|---|---|---|
| video editor | 76.38 | 12.02 | 13.11 | 9.57 | 11.45 | True |
| graphic designer | 71.66 | 14.39 | 12.38 | 13.06 | 14.10 | True |
| virtual assistant | 56.79 | 12.38 | 14.21 | 6.57 | 7.22 | True |
| social media manager | 38.76 | 16.64 | 12.76 | 7.68 | 5.69 | False |
| full stack developer | 23.17 | 22.85 | 27.42 | 6.05 | 6.90 | True |
| ui ux designer | 18.03 | 28.85 | 17.53 | 5.78 | 4.09 | False |
| web developer | 17.17 | 33.64 | 24.42 | 7.89 | 6.81 | False |
| youtube video editor | 16.79 | 29.75 | 39.78 | 4.82 | 6.68 | True |
| wordpress developer | 16.62 | 25.29 | 40.63 | 4.17 | 6.88 | True |
| content writer | 14.21 | 71.47 | 92.28 | 5.35 | 5.36 | True |
| logo designer | 12.45 | 56.94 | 72.00 | 6.19 | 7.28 | True |
| seo specialist | 11.97 | 40.96 | 56.43 | 3.50 | 4.88 | True |
| seo expert | 11.41 | 40.56 | 78.33 | 3.69 | 7.26 | True |
| expert | 10.59 | 25.82 | 31.24 | 3.21 | 4.54 | True |
| web designer | 10.38 | 29.13 | 27.68 | 3.93 | 3.84 | False |

Caveat: ~5 weeks of history means the weekly pattern is learned from only ~5 cycles and the trend is short-term. Raw counts are also bounded by the feed's daily scrape volume, so treat ranks and relative growth as more reliable than absolute levels.