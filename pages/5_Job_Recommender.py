import streamlit as st
import app_utils as U

U.setup("Task 5 - Job recommender", "🎯", "Describe your skills or the role you want; we match them against current postings.")
rec = U.get_recommender()
m = rec.meta()
st.caption(f"{m['n_jobs']:,} current postings indexed ({m['date_range'][0][:10]} to {m['date_range'][1][:10]}).")

with st.form("f"):
    q = st.text_input("Skills or role", placeholder="e.g. python data scientist, shopify developer, video editor")
    c = st.columns(4)
    country = c[0].selectbox("Client country", ["Any"] + m["countries"])
    jt = c[1].selectbox("Contract type", ["Any", "Hourly", "Fixed price"])
    min_rate = c[2].number_input("Minimum pay (USD/h or budget)", min_value=0.0, value=0.0, step=5.0)
    n = c[3].slider("Results", 5, 30, 10)
    remote = st.checkbox("Remote-titled postings only")
    go = st.form_submit_button("Recommend", type="primary")

if go:
    if not q.strip():
        st.warning("Enter some skills or a role first.")
    else:
        res = rec.recommend(q, top_n=n, country=None if country == "Any" else country,
                            job_type={"Hourly": "hourly", "Fixed price": "fixed"}.get(jt), min_rate=min_rate or None, remote_only=remote)
        if not res:
            st.info("No matches. Try broader keywords or fewer filters.")
        for r in res:
            pay = f"${r['hourly_low'] or '?'}-${r['hourly_high'] or '?'}/h" if r["is_hourly"] else (f"${r['budget']:,.0f} fixed" if r["budget"] else "budget not stated")
            with st.container(border=True):
                st.markdown(f"**[{r['title']}]({r['link']})**")
                st.caption(f"{pay} · {r['country']} · {r['category']} · match score {r['score']}")
U.note("Content-based: TF-IDF title similarity (70%) + category match (15%) + recency (10%) + pay fit (5%). Repeated generic titles are collapsed.")
