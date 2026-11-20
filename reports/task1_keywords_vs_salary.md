# Task 1 - Job-title keywords vs offered pay

Method: binary uni/bi-gram indicators (min 100 postings) -> per-keyword Mann-Whitney U test (Bonferroni-adjusted) and point-biserial correlation with log pay, plus a joint Ridge regression (5-fold CV R2) so overlapping keywords are not double-counted.


## Hourly rate

Jobs analysed: 102,253. Keywords tested: 903; significant (p_adj<0.01): 403. Ridge CV R2 using title keywords alone: **0.244**.


**Keywords associated with HIGHER pay**


| keyword | n_jobs | median_with | median_without | corr_log_pay | p_adj |
|---|---|---|---|---|---|
| consultant | 911 | 40.00 | 22.50 | 0.08 | 0.00 |
| attorney | 188 | 100.00 | 22.50 | 0.07 | 0.00 |
| lawyer | 217 | 90.00 | 22.50 | 0.07 | 0.00 |
| tax | 656 | 50.00 | 22.50 | 0.07 | 0.00 |
| videographer | 410 | 42.50 | 22.50 | 0.07 | 0.00 |
| independent | 109 | 200.00 | 22.50 | 0.06 | 0.00 |
| consultation | 341 | 49.50 | 22.50 | 0.06 | 0.00 |
| engineer | 1526 | 31.00 | 22.50 | 0.05 | 0.00 |
| cryptocurrency | 234 | 55.00 | 22.50 | 0.05 | 0.00 |
| expert | 7194 | 25.00 | 22.50 | 0.05 | 0.00 |
| financial | 563 | 37.50 | 22.50 | 0.05 | 0.00 |
| developer | 7767 | 25.00 | 22.50 | 0.05 | 0.00 |


**Keywords associated with LOWER pay**


| keyword | n_jobs | median_with | median_without | corr_log_pay | p_adj |
|---|---|---|---|---|---|
| assistant | 4219 | 8.50 | 22.50 | -0.21 | 0.00 |
| virtual | 2694 | 7.50 | 22.50 | -0.19 | 0.00 |
| virtual assistant | 2090 | 7.00 | 22.50 | -0.18 | 0.00 |
| va | 780 | 6.00 | 22.50 | -0.13 | 0.00 |
| lead | 1578 | 10.00 | 22.50 | -0.10 | 0.00 |
| cold | 1054 | 8.00 | 22.50 | -0.10 | 0.00 |
| lead generation | 938 | 8.00 | 22.50 | -0.09 | 0.00 |
| generation | 1083 | 9.50 | 22.50 | -0.09 | 0.00 |
| data entry | 865 | 7.50 | 22.50 | -0.09 | 0.00 |
| entry | 994 | 10.00 | 22.50 | -0.09 | 0.00 |
| social media | 3792 | 16.50 | 22.50 | -0.08 | 0.00 |
| appointment | 780 | 8.00 | 22.50 | -0.08 | 0.00 |



## Fixed-price budget

Jobs analysed: 103,737. Keywords tested: 982; significant (p_adj<0.01): 407. Ridge CV R2 using title keywords alone: **0.187**.


**Keywords associated with HIGHER pay**


| keyword | n_jobs | median_with | median_without | corr_log_pay | p_adj |
|---|---|---|---|---|---|
| development | 2221 | 300.00 | 100.00 | 0.10 | 0.00 |
| developer | 5943 | 150.00 | 100.00 | 0.09 | 0.00 |
| sales | 1398 | 250.00 | 100.00 | 0.07 | 0.00 |
| build | 1732 | 200.00 | 100.00 | 0.06 | 0.00 |
| expensify | 491 | 500.00 | 100.00 | 0.06 | 0.00 |
| engineer | 643 | 300.00 | 100.00 | 0.06 | 0.00 |
| high ticket | 111 | 3,000.00 | 100.00 | 0.06 | 0.00 |
| manager | 1535 | 200.00 | 100.00 | 0.06 | 0.00 |
| app | 4188 | 107.50 | 100.00 | 0.05 | 0.00 |
| stack | 719 | 300.00 | 100.00 | 0.05 | 0.00 |
| web | 2561 | 150.00 | 100.00 | 0.05 | 0.00 |
| saas | 478 | 325.00 | 100.00 | 0.05 | 0.00 |


**Keywords associated with LOWER pay**


| keyword | n_jobs | median_with | median_without | corr_log_pay | p_adj |
|---|---|---|---|---|---|
| need | 5725 | 50.00 | 100.00 | -0.08 | 0.00 |
| speakers | 506 | 10.00 | 100.00 | -0.08 | 0.00 |
| recording | 699 | 15.00 | 100.00 | -0.07 | 0.00 |
| logo | 3458 | 50.00 | 100.00 | -0.07 | 0.00 |
| recording project | 281 | 9.00 | 100.00 | -0.06 | 0.00 |
| fix | 1040 | 30.00 | 100.00 | -0.06 | 0.00 |
| edit | 851 | 25.00 | 100.00 | -0.06 | 0.00 |
| english | 2230 | 39.00 | 100.00 | -0.06 | 0.00 |
| quick | 720 | 25.00 | 100.00 | -0.05 | 0.00 |
| image | 940 | 30.00 | 100.00 | -0.05 | 0.00 |
| thumbnail | 615 | 20.00 | 100.00 | -0.05 | 0.00 |
| phrases | 119 | 5.00 | 100.00 | -0.05 | 0.00 |



Interpretation: correlation, not causation. Keywords are a weak-to-moderate predictor of pay; the R2 above says how much variance titles alone explain.