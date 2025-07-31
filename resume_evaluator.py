def evaluate_resume(parsed):
    """
    Mock resume evaluator.
    Returns dummy scores and keyword analysis matching your real output schema.
    """
    # Dummy keyword match structure
    keyword_match = {
        "score": 72.5,
        "matched_keywords": ["AWS", "Jenkins", "React", "TensorFlow"],
        "missing_keywords": ["Docker", "Kubernetes"]
    }
    # Dummy similarity scores
    similarity_score_tfidf = 0.82
    similarity_score_bert = 0.90
    
    # Compute a simple overall score (for demo)
    overall_score = round((keyword_match["score"] + similarity_score_tfidf*100 + similarity_score_bert*100) / 3, 2)

    return {
        "keyword_score": keyword_match["score"],
        "similarity_score_tfidf": similarity_score_tfidf,
        "similarity_score_bert": similarity_score_bert,
        "matched_keywords": keyword_match["matched_keywords"],
        "missing_keywords": keyword_match["missing_keywords"],
        "overall_score": overall_score
    }

