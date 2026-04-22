import pandas as pd
from typing import List, Dict
from . import analyzer, scorer


def load_resume_csv(path: str, nrows: int = None) -> pd.DataFrame:
    """Load resumes CSV into a pandas DataFrame.
    Assumes columns ['ID','Resume_str','Resume_html','Category'].
    Pass `nrows` to limit the number of rows read (useful for big files).
    """
    try:
        if nrows:
            df = pd.read_csv(path, nrows=nrows)
        else:
            df = pd.read_csv(path)
    except Exception as e:
        raise FileNotFoundError(f"Could not read CSV {path}: {e}")
    return df


def analyze_dataset(path: str, top_n: int = 5, job_description: str = "") -> List[Dict]:
    """Analyze first `top_n` resumes from a dataset file (optimized with batch processing).
    Returns a list of result dicts similar to what the web API produces.
    """
    df = load_resume_csv(path, nrows=top_n)
    results = []
    
    if job_description:
        jd_text = analyzer.preprocess_text(job_description)
        resumes_text = [analyzer.preprocess_text(str(row)) for row in df['Resume_str']]
        sims = scorer.calculate_similarity_batch(resumes_text, jd_text)
    
    for idx, (_, row) in enumerate(df.iterrows()):
        text = analyzer.preprocess_text(str(row.get('Resume_str', '')))
        entry = {
            'ID': row.get('ID'),
            'category': row.get('Category'),
            'skill_match': None,
            'missing_keywords': None,
            'similarity': None,
            'job_suitability_score': None,
            'ats_score': None,
            'best_suited_roles': None,
            'resume_errors': analyzer.detect_errors(text),
            'suggested_improvements': analyzer.suggest_improvements(text),
        }
        if job_description:
            entry['skill_match'] = analyzer.calculate_skill_match(text, jd_text)
            entry['missing_keywords'] = analyzer.find_missing_keywords(text, jd_text)
            entry['similarity'] = sims[idx] * 100
            entry['job_suitability_score'] = round(entry['similarity'], 2)
            entry['ats_score'] = analyzer.compute_ats_score(text, jd_text)
        else:
            entry['best_suited_roles'] = analyzer.best_suited_roles(text)
            entry['ats_score'] = analyzer.compute_ats_score(text)
        results.append(entry)
    return results


def rank_resumes_against_jd(path: str, job_description: str, top_n: int = 10) -> pd.DataFrame:
    """Load dataset and return DataFrame sorted by similarity (batch processed for speed)."""
    df = load_resume_csv(path)
    if df.empty:
        return df
    
    jd_text = analyzer.preprocess_text(job_description)
    
    # Preprocess all resumes at once
    resumes_text = [analyzer.preprocess_text(str(row)) for row in df['Resume_str']]
    
    # Batch calculate all similarities at once (much faster than iterating)
    sims = scorer.calculate_similarity_batch(resumes_text, jd_text)
    
    # Calculate ATS scores
    ats_scores = [analyzer.compute_ats_score(text, jd_text) for text in resumes_text]
    
    df['similarity'] = sims
    df['ats_score'] = ats_scores
    df = df.sort_values('similarity', ascending=False)
    return df.head(top_n)
