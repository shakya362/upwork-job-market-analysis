# Task 2 - Emerging job categories

Windows compared (14 days each, weekday-balanced): **A = 2024-02-17..2024-03-01**, **B = 2024-03-09..2024-03-22**. Share = category's fraction of all postings that day, which removes the effect of overall volume. Categories are keyword-derived from titles (the CSV has no category field).


## Categories ranked by share growth


| category | share_A_% | share_B_% | growth_% | slope_pp_per_week | ab_p |
|---|---|---|---|---|---|
| AI / Machine Learning | 2.20 | 2.44 | 11.01 | 0.08 | 0.00 |
| Software / DevOps | 4.00 | 4.38 | 9.48 | 0.13 | 0.00 |
| Sales / Lead Gen | 3.61 | 3.80 | 5.17 | 0.06 | 0.04 |
| Engineering / Other Tech | 0.82 | 0.85 | 4.18 | 0.00 | 0.43 |
| Design / Creative | 10.92 | 11.32 | 3.61 | 0.11 | 0.01 |
| Web Development | 16.25 | 16.80 | 3.40 | 0.20 | 0.00 |
| SEO / Marketing | 8.88 | 9.14 | 2.94 | 0.06 | 0.06 |
| Video / Audio | 8.56 | 8.81 | 2.83 | 0.04 | 0.07 |
| Customer Support | 1.20 | 1.21 | 1.10 | 0.02 | 0.80 |
| Finance / Legal | 1.61 | 1.61 | 0.57 | 0.02 | 0.88 |
| Admin / Virtual Assistant | 4.10 | 4.08 | -0.42 | -0.01 | 0.86 |
| Other | 22.82 | 22.63 | -0.82 | 0.00 | 0.35 |
| Mobile Apps | 2.84 | 2.78 | -1.92 | 0.00 | 0.49 |
| Data / Analytics | 4.96 | 4.42 | -10.81 | -0.19 | 0.00 |
| Writing / Content | 5.44 | 4.45 | -18.09 | -0.34 | 0.00 |
| Translation | 1.80 | 1.26 | -29.75 | -0.18 | 0.00 |


**Flagged emerging** (growth >5%, two-proportion p<0.01, positive weekday-adjusted trend): AI / Machine Learning, Software / DevOps


## Emerging title keywords (Bonferroni p<0.01, growing)


| keyword | jobs_A | jobs_B | per_1k_A | per_1k_B | growth_% |
|---|---|---|---|---|---|
| solana | 52 | 119 | 0.59 | 1.39 | 136.47 |
| subscription | 67 | 137 | 0.75 | 1.59 | 111.29 |
| shopping | 76 | 151 | 0.86 | 1.76 | 105.30 |
| monetization | 72 | 136 | 0.81 | 1.58 | 95.18 |
| crypto | 300 | 447 | 3.38 | 5.20 | 53.96 |


## Fading title keywords


| keyword | jobs_A | jobs_B | per_1k_A | per_1k_B | growth_% |
|---|---|---|---|---|---|
| copy paste | 259 | 34 | 2.92 | 0.40 | -86.44 |
| relationship | 125 | 35 | 1.41 | 0.41 | -71.07 |
| freelancers | 316 | 117 | 3.56 | 1.36 | -61.74 |
| general | 240 | 102 | 2.70 | 1.19 | -56.08 |
| languages | 113 | 49 | 1.27 | 0.57 | -55.19 |
| paste | 354 | 154 | 3.99 | 1.79 | -55.05 |
| jobs | 144 | 64 | 1.62 | 0.74 | -54.08 |
| money | 161 | 81 | 1.81 | 0.94 | -48.01 |
| data entry | 918 | 477 | 10.34 | 5.55 | -46.31 |
| writer needed | 229 | 122 | 2.58 | 1.42 | -44.95 |
| entry | 1052 | 574 | 11.85 | 6.68 | -43.62 |
| freelancer | 436 | 242 | 4.91 | 2.82 | -42.65 |


Caveat: the data spans about 6 weeks, so 'emerging' means short-term momentum, not a long-run trend.