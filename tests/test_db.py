import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
import db


@pytest.fixture
def fresh_db(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "test.db")
    db.init_db()
    yield db


def test_add_and_list_application(fresh_db):
    fresh_db.add_application("Stripe", "SWE Intern", "applied", "via LinkedIn")
    applications = fresh_db.list_applications()
    assert len(applications) == 1
    assert applications[0]["company"] == "Stripe"
    assert applications[0]["status"] == "applied"


def test_update_status(fresh_db):
    fresh_db.add_application("Google", "SWE Intern", "applied", "")
    app_id = fresh_db.list_applications()[0]["id"]
    fresh_db.update_status(app_id, "interviewing")
    assert fresh_db.list_applications()[0]["status"] == "interviewing"


def test_delete_application(fresh_db):
    fresh_db.add_application("Meta", "SWE Intern", "applied", "")
    app_id = fresh_db.list_applications()[0]["id"]
    fresh_db.delete_application(app_id)
    assert fresh_db.list_applications() == []


def test_count_by_status(fresh_db):
    fresh_db.add_application("A", "Role1", "applied", "")
    fresh_db.add_application("B", "Role2", "interviewing", "")
    fresh_db.add_application("C", "Role3", "applied", "")
    counts = fresh_db.count_by_status()
    assert counts["applied"] == 2
    assert counts["interviewing"] == 1


def test_upsert_job_posting_avoids_duplicates(fresh_db):
    job = {
        "external_id": "123", "company": "Acme", "position": "Backend Intern",
        "description": "Python and SQL", "url": "https://example.com", "tags": "python,sql",
    }
    fresh_db.upsert_job_posting(job)
    fresh_db.upsert_job_posting(job)  # same external_id again
    postings = fresh_db.list_job_postings()
    assert len(postings) == 1


def test_update_match_score(fresh_db):
    job = {
        "external_id": "456", "company": "Acme", "position": "Backend Intern",
        "description": "Python and SQL", "url": "https://example.com", "tags": "python",
    }
    fresh_db.upsert_job_posting(job)
    posting_id = fresh_db.list_job_postings()[0]["id"]
    fresh_db.update_match_score(posting_id, 87.5)
    assert fresh_db.list_job_postings()[0]["match_score"] == 87.5
