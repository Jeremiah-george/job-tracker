# Job Application Tracker (Streamlit edition)

A tool that tracks the internships/jobs you've applied to, and
automatically pulls in live postings and ranks them by how closely they
match your CV.

## Features

- Dashboard — log applications, see counts by status, change status
  inline, delete entries.
- Matches — fetches live postings from the free Remotive(https://remotive.com/api-documentation)
  API, It compares each job listing to your CV using TF-IDF and cosine similarity, a common text-matching technique, to score how well they fit.
  If a match looks good, you can log it as an application right from that result.

## Tech stack

Python, Streamlit, sqlite3 (standard library), scikit-learn, pytest.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Run it

```bash
streamlit run app.py
```

It opens automatically in your browser

## Run the tests

```bash
pytest
```

## Project structure

```
app.py           Streamlit UI - the whole app in one file
db.py            All database access, plain SQL via sqlite3
matching.py      TF-IDF matching logic
job_fetcher.py   Pulls postings from the Remotive API
cv.txt           Your CV as plain text (used for matching)
tests/
  test_db.py       Tests for the database functions
  test_matching.py Tests for the matching logic
```
