import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def extract_keywords(txt):
    txt = re.sub(r'[^a-zA-Z ]', '', txt.lower())
    return list(set(txt.split()))

def keywords_matcher(resume, job_des):
    resume_keywords = extract_keywords(resume)
    job_keywords = extract_keywords(job_des)

    match = list(set(resume_keywords).intersection(set(job_keywords)))
    score = len(match) / len(job_keywords) if job_keywords else 0

    return {
        'score' : round(score * 100, 2),
        'missing_keywords' :  list(set(job_keywords) - set(resume_keywords)),
        'matched_keywords' : match
    }

def similarity_scorer(resume, job_des):
    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform([resume, job_des])
    score = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
    return round(score * 100, 2)

def evaluator(resume, job_des):
    keyword_match = keywords_matcher(resume, job_des)
    similarity_score = similarity_scorer(resume, job_des)
    return {
        'keyword_score' : keyword_match['score'],
        'similarity_score' : similarity_score,
        'missing_keywords' : keyword_match['missing_keywords'],
        'matched_keywords' : keyword_match['matched_keywords']
    }