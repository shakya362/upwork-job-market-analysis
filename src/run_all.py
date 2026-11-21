"""Run every task end to end: python -m src.run_all"""
import time
from .common import load_clean
from . import (task1_keywords_salary as t1, task2_emerging as t2, task3_demand_forecast as t3, task4_country_rates as t4,
               task5_recommender as t5, task6_dashboard as t6, task7_remote as t7, task8_future_trends as t8)


def main():
    df = load_clean()
    print(f"Loaded {len(df):,} postings, {df.date.min():%Y-%m-%d} to {df.date.max():%Y-%m-%d}")
    for name, mod in [("Task 1", t1), ("Task 2", t2), ("Task 3", t3), ("Task 4", t4), ("Task 5", t5), ("Task 7", t7), ("Task 8", t8)]:
        t = time.time(); mod.run(df); print(f"{name} done in {time.time()-t:.1f}s")
    t6.build(df); print("Task 6 dashboard built")
    print("Task 5 offline check:", t5.evaluate(df))


if __name__ == "__main__":
    main()
