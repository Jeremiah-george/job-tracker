import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from matching import score_jobs


def test_score_jobs_ranks_closer_match_higher():
    cv_text = "Python developer experienced with FastAPI, SQL, and REST APIs"
    jobs = [
        "Looking for a Python backend engineer skilled in FastAPI and REST APIs",
        "Seeking a graphic designer experienced in Adobe Photoshop and Illustrator",
    ]
    scores = score_jobs(cv_text, jobs)
    assert scores[0] > scores[1]


def test_score_jobs_handles_empty_cv():
    assert score_jobs("", ["some job description"]) == [0.0]


def test_score_jobs_handles_no_jobs():
    assert score_jobs("some cv text", []) == []


def test_score_jobs_returns_values_between_0_and_1():
    scores = score_jobs("python sql apis", ["python backend role", "unrelated cooking recipes"])
    assert all(0.0 <= s <= 1.0 for s in scores)
