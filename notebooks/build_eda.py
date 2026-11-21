"""Builds and executes notebooks/01_eda.ipynb  (python notebooks/build_eda.py)"""
import nbformat as nbf
from nbclient import NotebookClient
from pathlib import Path

nb = nbf.v4.new_notebook()
C = []
md = lambda s: C.append(nbf.v4.new_markdown_cell(s.strip()))
code = lambda s: C.append(nbf.v4.new_code_cell(s.strip()))

md("""
# Exploratory Data Analysis: Upwork job postings (Feb-Mar 2024)

**Project:** Job Market Analysis and Recommendation System (Next Hikes)
**Data:** `all_upwork_jobs_2024-02-07-2024-03-24.csv`, about 245k postings scraped from Upwork's RSS feed.

This notebook answers the questions that decide *how* the eight project tasks can be done:

1. What does each column contain, and how much of it is usable?
2. What time window is trustworthy, and what artefacts does the scrape introduce?
3. What do pay, contract type, geography and titles look like?
4. What do the findings mean for the eight tasks?

Every cleaning rule used by the pipeline (`src/common.py`) is justified here.
""")

code("""
import sys, warnings
sys.path.insert(0, "..")
warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
import matplotlib.pyplot as plt, seaborn as sns
from src.common import load_raw, load_clean, CATEGORY_RULES

sns.set_theme(style="whitegrid", context="notebook")
plt.rcParams["figure.dpi"] = 110
pd.options.display.float_format = "{:,.2f}".format
raw = load_raw()
""")

md("## 1. Raw data: structure and completeness")
code("""
print(f"Rows: {len(raw):,}   Columns: {raw.shape[1]}")
print(f"Duplicate links: {raw.link.duplicated().sum():,}")
print(f"Postings whose exact title appears more than once: {raw.title.duplicated(keep=False).mean():.1%}")
summary = pd.DataFrame({"dtype": raw.dtypes.astype(str), "missing_%": raw.isna().mean() * 100, "unique": raw.nunique()})
summary
""")
md("""
**Reading the table**

- Eight columns only: title, link, date, contract type, hourly low/high, fixed budget and client country. There is **no description, skills list, category, experience level or location requirement**. That limits Tasks 2, 5 and 7: categories and remote signals have to be inferred from the *title text*.
- No duplicate links, so every row is a distinct posting URL.
- The 58-60% missing rate in the pay columns is not a data-quality problem. It is structural: hourly jobs carry `hourly_low/high`, fixed-price jobs carry `budget`. We verify that next.
- Country is missing for only about 2% of rows.
""")

code("""
h, f = raw[raw.is_hourly], raw[~raw.is_hourly]
check = pd.DataFrame({
    "rows": [len(h), len(f)],
    "has hourly_low %": [h.hourly_low.notna().mean() * 100, f.hourly_low.notna().mean() * 100],
    "has hourly_high %": [h.hourly_high.notna().mean() * 100, f.hourly_high.notna().mean() * 100],
    "has budget %": [h.budget.notna().mean() * 100, f.budget.notna().mean() * 100],
}, index=["hourly jobs", "fixed-price jobs"])
check
""")
md("""
**Confirmed:** fixed-price jobs essentially always have a budget and never an hourly range, and hourly jobs never have a budget. The two pay types must be analysed **separately**; mixing hourly rates and fixed budgets in one number would be meaningless. About 27% of hourly jobs advertise no rate at all and about 3% give only a minimum, so rate analysis uses roughly 100k of the 141k hourly jobs.
""")

md("## 2. Time coverage and scrape artefacts")
code("""
raw["date"] = pd.to_datetime(raw.published_date, utc=True).dt.tz_localize(None).dt.normalize()
daily = raw.groupby("date").size()
fig, ax = plt.subplots(figsize=(11, 3.8))
ax.bar(daily.index, daily.values, width=0.9, color="#2a6f97")
ax.set_yscale("log"); ax.set_ylabel("postings per day (log scale)")
ax.set_title("Daily postings in the raw file")
for d, txt in [("2024-02-15", "15 Feb: scrape gap"), ("2024-03-24", "24 Mar: partial day")]:
    ax.annotate(txt, (pd.Timestamp(d), daily[pd.Timestamp(d)]), xytext=(0, 25), textcoords="offset points", ha="center", arrowprops=dict(arrowstyle="->"), fontsize=8)
plt.tight_layout(); plt.show()
dense = daily[daily > 100]
print(f"Dense window: {dense.index.min():%Y-%m-%d} to {dense.index.max():%Y-%m-%d} ({len(dense)} days)")
print(f"Rows outside the dense window: {daily[daily <= 100].sum():,} (earliest {daily.index.min():%Y-%m-%d})")
print(f"Median postings/day in window: {dense.median():,.0f}   max: {dense.max():,}")
""")
md("""
**Findings**

- The file name says 7 Feb to 24 Mar, but real coverage starts on **13 Feb**. The few hundred earlier rows are stragglers with old publish dates, so the pipeline keeps only the dense window.
- **15 Feb has about a quarter of a normal day's volume**: a scrape outage. **24 Mar is cut off mid-day.** The forecasting tasks therefore train on 16 Feb to 22 Mar (36 clean days), roughly five weeks. That is too short for yearly seasonality or long-run trends, so forecasts are limited to a few weeks ahead.
- Weekday volume plateaus at about 7,000 per day and never exceeds about 7,500. That flat ceiling suggests the RSS feed returns a **capped number of items**, not that Upwork posts exactly 7k jobs a day. Absolute counts are therefore less trustworthy than **shares and growth rates**, which is why Tasks 2 and 8 work with shares.
""")

code("""
df = load_clean()
dow = df.groupby([df.date.dt.dayofweek]).size() / df.groupby(df.date.dt.dayofweek).date.nunique()
dow.index = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
ax = dow.plot.bar(figsize=(6, 3), color="#468faf", rot=0)
ax.set_ylabel("avg postings/day"); ax.set_title("Weekly rhythm"); plt.tight_layout(); plt.show()
print(f"Weekend volume is {dow[['Sat','Sun']].mean() / dow[['Mon','Tue','Wed','Thu','Fri']].mean():.0%} of the weekday level")
""")
md("""
There is a clear **weekly cycle**: weekends run well below weekdays. Any time-series model must include day-of-week effects, otherwise a Saturday would look like a collapse in demand. This is why Tasks 3, 7 and 8 use weekday dummies. Comparison windows in Task 2 are chosen so each weekday appears equally often.
""")

md("## 3. Cleaning decisions")
code("""
rules = pd.DataFrame({
    "rule": ["Keep dense date window (13 Feb-24 Mar)", "Hourly rate outside $3-$300 set to missing", "Swap hourly low/high when low > high", "Fixed budget outside $5-$100,000 set to missing"],
    "rows affected": [
        len(raw) - len(df),
        int(((raw[["hourly_low", "hourly_high"]] < 3) | (raw[["hourly_low", "hourly_high"]] > 300)).any(axis=1).sum()),
        int((raw.hourly_low > raw.hourly_high).sum()),
        int(((raw.budget < 5) | (raw.budget > 100_000)).sum()),
    ]})
rules
""")
md("""
These rules touch a small fraction of rows (the low/high swap affects none today and stays as a safeguard for future months). The thresholds are judgement calls: sub-$3 hourly rates and rates near $999 look like placeholders, and the project is about realistic offers. The extreme budget cap matters most, because a single $1,000,000 posting would otherwise dominate any mean.
""")

md("## 4. Pay distributions")
code("""
hh = df[df.is_hourly].hourly_mid.dropna()
ff = df[~df.is_hourly].budget.dropna()
fig, ax = plt.subplots(1, 2, figsize=(11, 3.8))
sns.histplot(hh, bins=60, ax=ax[0], color="#2a9d8f"); ax[0].axvline(hh.median(), color="k", ls="--", lw=1)
ax[0].set_title("Hourly rate (midpoint of range, USD/h)"); ax[0].set_xlim(0, 150)
sns.histplot(np.log10(ff), bins=60, ax=ax[1], color="#e9c46a"); ax[1].axvline(np.log10(ff.median()), color="k", ls="--", lw=1)
ax[1].set_xlabel("log10(budget USD)"); ax[1].set_title("Fixed-price budget (log scale)")
plt.tight_layout(); plt.show()
print(pd.DataFrame({"hourly": hh.describe(), "fixed": ff.describe()}).round(1))
print(f"\\nHourly: mean/median = {hh.mean()/hh.median():.2f}   Fixed: mean/median = {ff.mean()/ff.median():.2f}")
print(f"Budgets that are multiples of 50: {(ff % 50 == 0).mean():.0%}   Hourly midpoints that are multiples of 5: {(hh % 5 == 0).mean():.0%}")
""")
md("""
**Findings**

- **Both distributions are right-skewed, fixed-price far more so.** The hourly mean is about 25% above its median, while the fixed-price mean is almost six times its median because a few large projects pull it up. **Medians are the right summary statistic** for every comparison in this project, and the keyword and country tasks use log pay or rank-based tests for the same reason.
- The typical posting is small: the median hourly rate is about **$22.50/h** and the median fixed budget is about **$100**. A quarter of fixed-price jobs offer $25 or less.
- Budgets cluster on round numbers (more than half are multiples of $50), so pay behaves partly like a **categorical price point**, not a smooth variable. That is another reason to prefer rank-based tests over t-tests.
""")

code("""
ranges = df[df.is_hourly & df.hourly_low.notna() & df.hourly_high.notna()]
width = (ranges.hourly_high - ranges.hourly_low)
rel = width / ranges.hourly_mid
print(f"Hourly postings with a full range: {len(ranges):,}")
print(f"Median range width: ${width.median():.1f}/h   median width relative to midpoint: {rel.median():.0%}")
print(f"Ranges where low == high: {(width == 0).mean():.1%}")
""")
md("""
Clients usually post a **range**, not a single rate, and the range is wide relative to its midpoint. We use the **midpoint** as the single "offered rate" and report it as an *advertised* rate. This is a poster's budget signal, not what a freelancer ends up earning.
""")

md("## 5. Categories (derived from titles) and how pay differs")
code("""
cat = df.groupby("category").agg(
    postings=("title", "size"), hourly_share=("is_hourly", "mean"),
    median_hourly=("hourly_mid", "median"), median_fixed=("budget", "median")).sort_values("postings", ascending=False)
cat["share_%"] = cat.postings / cat.postings.sum() * 100
cat["hourly_share"] *= 100
display(cat[["postings", "share_%", "hourly_share", "median_hourly", "median_fixed"]])
fig, ax = plt.subplots(1, 2, figsize=(11, 4.5), sharey=True)
order = cat.sort_values("median_hourly").index
sns.barplot(x=cat.loc[order, "median_hourly"], y=order, ax=ax[0], color="#2a9d8f"); ax[0].set_title("Median hourly rate (USD/h)"); ax[0].set_ylabel("")
sns.barplot(x=cat.loc[order, "median_fixed"], y=order, ax=ax[1], color="#e9c46a"); ax[1].set_title("Median fixed budget (USD)")
plt.tight_layout(); plt.show()
""")
md("""
**Findings**

- The keyword rules label about three-quarters of postings. **"Other" is still the largest single bucket** (about 23%), so categories are a pragmatic approximation, not a clean taxonomy. Improving the rules, or replacing them with embeddings, would be the first upgrade.
- **Web Development is the biggest labelled category (about 17%)**, followed by Design/Creative, SEO/Marketing and Video/Audio. These four make up about 45% of all postings.
- **Pay differs sharply by category.** Finance/Legal, Software/DevOps and AI/ML sit at the top of the hourly ranking, while Sales/Lead Gen and Admin/Virtual Assistant sit at the bottom (roughly $10-12/h). The cheapest fields are also the ones where hourly contracts are most common (Admin/VA is about three-quarters hourly), whereas Mobile Apps, Video and Design are closer to half and half.
- Fixed budgets rank differently from hourly rates (Translation and Video are cheapest; Admin and Sales look expensive). One possible explanation is that fixed-price jobs in those fields are larger, ongoing packages (the data cannot confirm this). Either way, **hourly and fixed pay cannot be compared across categories on one scale**.
""")

md("## 6. Geography")
code("""
ct = df.country.value_counts()
top = ct.head(12)
fig, ax = plt.subplots(figsize=(8, 3.8))
sns.barplot(x=top.values, y=top.index, color="#264653", ax=ax); ax.set_title("Postings by client country"); ax.set_xlabel("postings")
plt.tight_layout(); plt.show()
print(f"Countries: {df.country.nunique()-1}   US share: {ct['United States']/len(df):.1%}   Top-5 share: {ct.head(5).sum()/len(df):.1%}   Unknown: {ct.get('Unknown',0)/len(df):.1%}")
big = df[df.is_hourly & df.hourly_mid.notna() & df.country.isin(ct[ct >= 2000].index) & (df.country != 'Unknown')]
order = big.groupby("country").hourly_mid.median().sort_values().index
fig, ax = plt.subplots(figsize=(8, 4.8))
sns.boxplot(data=big, x="hourly_mid", y="country", order=order, showfliers=False, color="#8ecae6", ax=ax)
ax.set_xlabel("advertised hourly rate (USD/h)"); ax.set_title("Hourly rate spread, countries with 2,000+ postings"); ax.set_ylabel("")
plt.tight_layout(); plt.show()
""")
md("""
**Findings**

- Demand is **heavily concentrated in the US (about 41% of postings)**, with the top five countries accounting for about 65%. A global map (Task 4) will therefore be mostly empty or noisy in the tail. That is why Task 4 only reports countries with 30 or more rated postings, and attaches bootstrap confidence intervals.
- The country is the **client's** country, not the freelancer's. The rate map shows what clients in each country offer, not what freelancers in each country earn.
- Spread *within* a country is large compared with the gaps *between* the biggest markets. Median rates differ by only a few dollars between the US ($25), UK and Germany ($22.50 each), and their interquartile ranges overlap heavily (roughly $15 to $35-40). Country is informative but far from decisive for pay.
""")

md("## 7. Titles: the only text we have")
code("""
tl = df.title.str.split().str.len()
print(f"Title length in words: median {tl.median():.0f}, 90th percentile {tl.quantile(.9):.0f}")
rep = df.title_clean.value_counts()
print(f"Postings sharing an identical title with another posting: {(df.title_clean.map(rep) > 1).mean():.1%}")
print("\\nMost repeated titles:"); print(rep.head(8).to_string())
from sklearn.feature_extraction.text import CountVectorizer
cv = CountVectorizer(stop_words="english", min_df=50, token_pattern=r"(?u)\\b[a-zA-Z][a-zA-Z0-9+#.]+\\b")
X = cv.fit_transform(df.title_clean)
words = pd.Series(np.asarray(X.sum(0)).ravel(), index=cv.get_feature_names_out()).sort_values(ascending=False).head(20)
ax = words.sort_values().plot.barh(figsize=(6, 5), color="#6a994e"); ax.set_title("Most common title words"); plt.tight_layout(); plt.show()
""")
md("""
**Findings**

- Titles are short (a handful of words), so there is little text to model. Bag-of-words and TF-IDF are appropriate; deep language models would have little to learn from.
- About a quarter of postings share their exact title with at least one other posting. Generic titles ("Social Media Manager", "Logo Design", "Video Editor") are legitimately common, and some repeats may be templated or re-posted jobs (the data cannot tell which). The **recommender collapses duplicate titles** so one popular title does not fill the whole result list.
- The most common words are "needed", "website", "developer", "expert", "video" and "design". Filler such as "needed", "expert" and "looking" says little about the work, so Task 1 uses stop-word filtering and requires keywords to appear in at least 100 postings before testing them.
""")

md("## 8. Category mix over time")
code("""
d = df[(df.date >= "2024-02-16") & (df.date <= "2024-03-22")]
wk = d.groupby(["week", "category"]).size().unstack(fill_value=0)
wk = wk[(wk.sum(axis=1) > 30000)]  # complete weeks only
share = wk.div(wk.sum(axis=1), axis=0) * 100
focus = ["AI / Machine Learning", "Software / DevOps", "Web Development", "Writing / Content", "Translation", "Data / Analytics"]
ax = share[focus].plot(marker="o", figsize=(9, 4)); ax.set_ylabel("% of weekly postings"); ax.set_title("Weekly category share (complete weeks)")
ax.legend(fontsize=8, bbox_to_anchor=(1.01, 1), loc="upper left"); plt.tight_layout(); plt.show()
print((share[focus].iloc[-1] - share[focus].iloc[0]).round(2).rename("change in share, first to last complete week (pp)").to_string())
""")
md("""
Category shares move only slowly over five weeks, but a few move consistently in one direction: **AI/ML, Software/DevOps and Web Development drift up, while Writing, Translation and Data drift down**. Task 2 tests these shifts formally (two-proportion tests and weekday-adjusted trends) rather than trusting eyeballed lines, and Task 8 projects them with damped trends.
""")

md("## 9. The remote-work signal (and a flag I had to fix)")
code("""
import re
broad = re.compile(r"\\b(remote|work from home|wfh|virtual|telecommut\\w*|anywhere|distributed)\\b", re.I)
trigger = df.title.str.extract(broad)[0].str.lower()
print("First attempt (broad keyword list) matched %.2f%% of titles. What it matched on:" % (trigger.notna().mean() * 100))
print(trigger.value_counts().to_string())
virt = df.title[trigger == "virtual"].str.lower()
is_va = virt.str.contains(r"assistan|\\bva\\b|assitan|asisstan")
print("\\nOf the 'virtual' matches, %.0f%% are virtual-assistant style titles (assistant / assistance / VA)" % (is_va.mean() * 100))
print("Other 'virtual' examples:", virt[~is_va].sample(4, random_state=0).tolist())
""")
md("""
**Why this matters.** My first remote flag counted the word *virtual*, which produced a remote share of about 2.3%. About three-quarters of those hits were the word "virtual" itself, and the large majority of those are **Virtual Assistant job titles** (plus "virtual tour", "virtual desktop" and "virtual reality"). That is a job type, not a work arrangement. It also made "remote" jobs look cheap, because they inherited the low pay of VA work. The pipeline now uses a strict definition: *remote, remotely, work from home, WFH, telecommute, work from/anywhere*.
""")
code("""
print(f"Strict definition: {df.remote_mention.mean():.2%} of titles ({df.remote_mention.sum():,} postings); on-site/hybrid wording: {df.onsite_mention.mean():.2%}")
print("\\nSample remote-titled postings:")
for t in df[df.remote_mention].title.sample(8, random_state=2).tolist(): print(" -", t)
r, o = df[df.remote_mention], df[~df.remote_mention]
print("\\nHourly-contract share: remote-titled %.0f%% vs others %.0f%%" % (r.is_hourly.mean() * 100, o.is_hourly.mean() * 100))
print("Median hourly: remote-titled $%.1f vs others $%.1f" % (r.hourly_mid.median(), o.hourly_mid.median()))
print("Median fixed budget: remote-titled $%.0f vs others $%.0f" % (r.budget.median(), o.budget.median()))
""")
md("""
Under the strict definition only about **0.6% of titles** state a remote or work-from-home arrangement, and **every Upwork job is remote-style by nature**. So the share measures how often a client *chooses to emphasise* remote work, not how much remote work exists. Genuine remote job ads dominate the sample, with occasional technical false positives (for example "remote connection"), so treat the flag as a weak signal. Remote-titled postings lean towards hourly contracts and are not cheaper than others (the hourly gap is borderline and the fixed-budget gap is modest), the opposite of what the first flag suggested. Task 7 reports the strict version. A real remote-work analysis would need description text or a location-requirement field.
""")

md("""
## 10. Takeaways for the eight tasks

| Finding | Consequence |
|---|---|
| Hourly and fixed pay are separate, skewed, round-number distributions | Analyse them separately, use medians, logs and rank tests (Tasks 1, 4) |
| Only 5 clean weeks; 15 Feb outage; partial 24 Mar; flat ~7k/day ceiling | Train on 16 Feb-22 Mar, use shares, short horizons, damped trends (Tasks 2, 3, 8) |
| Strong weekday cycle | Weekday effects in every time-series model; balanced comparison windows (Tasks 2, 3, 7) |
| No category or description field; titles are short | Keyword-derived categories (23% "Other"); TF-IDF recommender (Tasks 2, 5) |
| US dominates; long tail of tiny countries | Minimum 30 postings per country plus bootstrap CIs (Task 4) |
| Only about 0.6% of titles state remote work; a broad keyword list wrongly matched "virtual assistant" | Strict remote definition; report it as an emphasis signal, not market size (Task 7) |
| Repeated titles are common | De-duplicate titles in the recommender (Task 5) |

**Next steps beyond this dataset:** collect more months so seasonality and genuine trends become estimable, add description and skills fields for better categories and a stronger recommender, and replace the keyword rules with embeddings.
""")

nb["cells"] = C
nb.metadata["kernelspec"] = {"display_name": "Python 3", "language": "python", "name": "python3"}
out = Path(__file__).parent / "01_eda.ipynb"
NotebookClient(nb, timeout=300, kernel_name="python3", resources={"metadata": {"path": str(out.parent)}}).execute()
nbf.write(nb, out)
print("wrote", out, f"{out.stat().st_size/1e6:.1f} MB")
