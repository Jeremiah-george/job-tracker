import re
from typing import List, Dict

import requests

REMOTIVE_API_URL = "https://remotive.com/api/remote-jobs"


def fetch_jobs(search: str = "software engineer intern", limit: int = 20) -> List[Dict]:
    params = {"search": search, "limit": limit}
    response = requests.get(REMOTIVE_API_URL, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()

    results = []
    for job in data.get("jobs", []):
        results.append(
            {
                "external_id": str(job.get("id")),
                "company": job.get("company_name", "Unknown") or "Unknown",
                "position": job.get("title", "Unknown") or "Unknown",
                "description": strip_html(job.get("description", ""))[:5000],
                "url": job.get("url", ""),
                "tags": ",".join(job.get("tags", []) or []),
            }
        )
    return results


def strip_html(raw_html: str) -> str:
    """Very small HTML tag stripper - Remotive descriptions come as HTML."""
    text = re.sub(r"<[^>]+>", " ", raw_html or "")
    return re.sub(r"\s+", " ", text).strip()
