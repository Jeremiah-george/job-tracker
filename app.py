"""
Job Application Tracker - Streamlit version.
"""
from pathlib import Path

import streamlit as st

import db
from job_fetcher import fetch_jobs
from matching import score_jobs

st.set_page_config(page_title="Job Application Tracker", page_icon="📋", layout="wide")
db.init_db()

CV_PATH = Path(__file__).resolve().parent / "cv.txt"
STATUSES = ["applied", "interviewing", "offer", "rejected"]


def read_cv_text() -> str:
    return CV_PATH.read_text() if CV_PATH.exists() else ""


st.sidebar.title("📋 Job Tracker")
page = st.sidebar.radio("Go to", ["Dashboard", "Matches"])

# Dashboard - your own logged applications

if page == "Dashboard":
    st.title("Your Applications")

    counts = db.count_by_status()
    cols = st.columns(4)
    for col, status in zip(cols, STATUSES):
        col.metric(status.capitalize(), counts.get(status, 0))

    st.subheader("Log a new application")
    with st.form("add_application", clear_on_submit=True):
        c1, c2 = st.columns(2)
        company = c1.text_input("Company")
        role = c2.text_input("Role")
        status = st.selectbox("Status", STATUSES)
        notes = st.text_input("Notes (optional)")
        if st.form_submit_button("Add"):
            if company and role:
                db.add_application(company, role, status, notes)
                st.rerun()
            else:
                st.warning("Company and role are required.")

    st.subheader("All applications")
    applications = db.list_applications()
    if not applications:
        st.info("No applications logged yet — add one above, or log one from the Matches page.")
    else:
        header = st.columns([2, 2, 2, 3, 1])
        for col, label in zip(header, ["Company", "Role", "Status", "Notes", ""]):
            col.markdown(f"**{label}**")

        for a in applications:
            c1, c2, c3, c4, c5 = st.columns([2, 2, 2, 3, 1])
            c1.write(a["company"])
            c2.write(a["role"])
            new_status = c3.selectbox(
                "Status", STATUSES, index=STATUSES.index(a["status"]),
                key=f"status_{a['id']}", label_visibility="collapsed",
            )
            if new_status != a["status"]:
                db.update_status(a["id"], new_status)
                st.rerun()
            c4.write(a["notes"] or "—")
            if c5.button("🗑️", key=f"delete_{a['id']}"):
                db.delete_application(a["id"])
                st.rerun()

# Matches - live postings scored against your CV
else:
    st.title("Job Matches")

    search = st.text_input("Search term", value="software engineer intern")
    if st.button("Fetch + Score"):
        try:
            fetched = fetch_jobs(search=search)
            for job in fetched:
                db.upsert_job_posting(job)
            st.success(f"Fetched {len(fetched)} postings.")
        except Exception as exc:
            st.warning(f"Couldn't fetch new postings right now ({exc}). Showing previously saved ones.")

    cv_text = read_cv_text()
    if not cv_text:
        st.warning("No CV text found — add your skills/experience to cv.txt to enable match scoring.")

    postings = db.list_job_postings()
    if cv_text and postings:
        scores = score_jobs(cv_text, [p["description"] for p in postings])
        for posting, score in zip(postings, scores):
            db.update_match_score(posting["id"], round(score * 100, 1))
        postings = db.list_job_postings()  # re-read, now sorted by the updated score

    if not postings:
        st.info("No postings yet — try fetching above.")
    else:
        for p in postings:
            with st.container(border=True):
                c1, c2 = st.columns([5, 1])
                c1.markdown(f"**{p['position']}** — {p['company']}")
                c1.caption(p["tags"])
                c1.write((p["description"] or "")[:250] + "...")
                c1.markdown(f"[View posting]({p['url']})")
                c2.metric("Match", f"{p['match_score']}%")
                if c2.button("Log application", key=f"log_{p['id']}"):
                    db.add_application(
                        p["company"], p["position"], "applied",
                        notes=f"Logged from Matches (score {p['match_score']}%)",
                        source_job_id=p["id"],
                    )
                    st.rerun()
