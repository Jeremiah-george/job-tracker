import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "job_tracker.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT NOT NULL,
            role TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'applied',
            date_applied TEXT NOT NULL,
            notes TEXT DEFAULT '',
            source_job_id INTEGER
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS job_postings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            external_id TEXT UNIQUE NOT NULL,
            company TEXT,
            position TEXT,
            description TEXT,
            url TEXT,
            tags TEXT,
            match_score REAL DEFAULT 0
        )
        """
    )
    conn.commit()
    conn.close()

# Applications

def add_application(company, role, status="applied", notes="", source_job_id=None):
    conn = get_connection()
    conn.execute(
        """INSERT INTO applications (company, role, status, date_applied, notes, source_job_id)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (company, role, status, datetime.utcnow().isoformat(timespec="seconds"), notes, source_job_id),
    )
    conn.commit()
    conn.close()


def list_applications():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM applications ORDER BY date_applied DESC").fetchall()
    conn.close()
    return rows


def update_status(app_id, status):
    conn = get_connection()
    conn.execute("UPDATE applications SET status = ? WHERE id = ?", (status, app_id))
    conn.commit()
    conn.close()


def delete_application(app_id):
    conn = get_connection()
    conn.execute("DELETE FROM applications WHERE id = ?", (app_id,))
    conn.commit()
    conn.close()


def count_by_status():
    conn = get_connection()
    rows = conn.execute("SELECT status, COUNT(*) AS c FROM applications GROUP BY status").fetchall()
    conn.close()
    return {row["status"]: row["c"] for row in rows}

# Job postings

def upsert_job_posting(job: dict):
    conn = get_connection()
    existing = conn.execute(
        "SELECT id FROM job_postings WHERE external_id = ?", (job["external_id"],)
    ).fetchone()
    if not existing:
        conn.execute(
            """INSERT INTO job_postings (external_id, company, position, description, url, tags, match_score)
               VALUES (?, ?, ?, ?, ?, ?, 0)""",
            (job["external_id"], job["company"], job["position"], job["description"], job["url"], job["tags"]),
        )
        conn.commit()
    conn.close()


def list_job_postings():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM job_postings ORDER BY match_score DESC").fetchall()
    conn.close()
    return rows


def update_match_score(job_id, score):
    conn = get_connection()
    conn.execute("UPDATE job_postings SET match_score = ? WHERE id = ?", (score, job_id))
    conn.commit()
    conn.close()
