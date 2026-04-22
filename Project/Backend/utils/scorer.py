from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Global vectorizer for faster reuse
_vectorizer = TfidfVectorizer(max_features=500, ngram_range=(1, 2))
_vectorizer_fitted = False


def calculate_similarity(resume: str, job_description: str) -> float:
    """Return cosine similarity between two pieces of text (0..1) using TF-IDF.
    
    Fast method optimized for batch processing.
    """
    try:
        vect = TfidfVectorizer(max_features=500, ngram_range=(1, 2))
        vect_matrix = vect.fit_transform([resume, job_description])
        sim = cosine_similarity(vect_matrix[0:1], vect_matrix[1:2])[0][0]
        return float(sim)
    except Exception:
        return 0.0


def calculate_similarity_batch(resumes: list, job_description: str) -> list:
    """Calculate similarity for multiple resumes against one JD (much faster).
    
    Returns list of similarity scores in same order as input resumes.
    """
    try:
        all_texts = [job_description] + resumes
        vect = TfidfVectorizer(max_features=500, ngram_range=(1, 2))
        vect_matrix = vect.fit_transform(all_texts)
        jd_vec = vect_matrix[0:1]
        resume_vecs = vect_matrix[1:]
        similarities = cosine_similarity(jd_vec, resume_vecs)[0]
        return [float(sim) for sim in similarities]
    except Exception:
        return [0.0] * len(resumes)
