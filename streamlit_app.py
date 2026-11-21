"""Home page. Run locally: streamlit run streamlit_app.py"""
import app_utils as U
import streamlit as st
import plotly.express as px

U.setup("Upwork Job Market Analysis", "🧭", "Job-market analytics and a recommendation engine built on ~245k Upwork postings (13 Feb - 24 Mar 2024).")
df = U.load_df()

c = st.columns(5)
c[0].metric("Postings analysed", f"{len(df):,}")
c[1].metric("Date range", f"{df.date.min():%d %b} - {df.date.max():%d %b %Y}")
c[2].metric("Hourly share", f"{df.is_hourly.mean():.0%}")
c[3].metric("Median hourly rate", f"${df.hourly_mid.median():.1f}")
c[4].metric("Client countries", f"{df.country.nunique() - 1}")

left, right = st.columns(2)
daily = df.groupby("date").size().reset_index(name="postings")
left.plotly_chart(px.bar(daily, x="date", y="postings", title="Postings per day (15 Feb = scrape gap, 24 Mar = partial)"), width="stretch")
cat = (df.category.value_counts(normalize=True) * 100).rename_axis("category").reset_index(name="share_%")
right.plotly_chart(px.bar(cat.sort_values("share_%"), x="share_%", y="category", orientation="h", title="Share of postings by category (%)"), width="stretch")

st.subheader("What is in this app")
st.markdown("""
| Page | Task | Question it answers |
|---|---|---|
| Keywords vs Pay | 1 | Which title words go with higher or lower pay? Look up any keyword. |
| Emerging Categories | 2 | Which categories and keywords are gaining share? |
| Demand Forecast | 3 | Which roles will be most in demand over the next 14 days? |
| Country Rates | 4 | How do advertised hourly rates differ by client country? |
| Job Recommender | 5 | Find matching postings for your skills, with filters. |
| Monthly Dashboard | 6 | Month-by-month KPIs and trends, with filters. |
| Remote Work | 7 | How often do titles stress remote work, and is it changing? |
| Future Trends | 8 | Cautious / baseline / optimistic 4-week scenarios. |
""")
with st.expander("Data caveats (read before quoting numbers)"):
    st.markdown("""
- The file has **no category, description or location-requirement field**. Categories are keyword rules on titles, and about 23% stay "Other".
- Dense coverage is only about **5.5 weeks**, so "emerging" means short-term momentum and forecasts run 2-4 weeks.
- Weekday volume plateaus near 7k/day, which suggests the feed was capped. **Shares and growth rates are safer than raw counts.**
- Rates are what clients **advertise** (midpoint of the range), not what freelancers earn. About 27% of hourly postings state no rate.
- "Remote" means the title says remote / work-from-home (about 0.6% of postings). Every Upwork job is remote-style, so this measures emphasis.
""")
