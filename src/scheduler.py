"""Tiny monthly scheduler for the `pipeline` container: runs at start, then on the 1st of each month."""
import time
from datetime import date
from .run_all import main

if __name__ == "__main__":
    last = None
    while True:
        key = (date.today().year, date.today().month)
        if key != last and (last is None or date.today().day >= 1):
            main(); last = key
        time.sleep(3600)
