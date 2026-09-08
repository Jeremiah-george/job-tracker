"""
Matches your CV against job descriptions using TF-IDF + cosine similarity.
"""
from typing import List

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def score_jobs(cv_text: str, job_descriptions: List[str]) -> List[float]:
    if not cv_text.strip() or not job_descriptions:
        return [0.0 for _ in job_descriptions]

    documents = [cv_text] + job_descriptions
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(documents)

    cv_vector = tfidf_matrix[0:1]
    job_vectors = tfidf_matrix[1:]

    similarities = cosine_similarity(cv_vector, job_vectors)[0]
    return similarities.tolist()
