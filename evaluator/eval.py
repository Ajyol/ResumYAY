import spacy
from nltk.sem.chat80 import items
from sentence_transformers import SentenceTransformer, util

nlp = spacy.load("en_core_web_sm", disable=["ner", "parser_scripts"])
model = SentenceTransformer('all-MiniLM-L12-v2')

def extract_keywords(txt):
    doc = nlp(txt.lower())
    return list({
        token.lemma_ for token in doc
        if token.pos_ in {"NOUN", "PROPN", "VERB", "ADJ"} and not token.is_stop
    })

def experience_scorer(resume, job_des):
    raw_text = resume.get("raw_text", "")
    experience = resume.get("experience", "")
    responsibilities = job_des.get("responsibilities", [])

    raw_text_emb = model.encode(raw_text, convert_to_tensor=True)
    exp_emb = model.encode(experience, convert_to_tensor=True)
    job_emb = model.encode(responsibilities, convert_to_tensor=True)

    matched_experience = []
    threshold = 0.7

    for i, resp_emb in enumerate(job_emb):
        sim_full = util.cos_sim(raw_text_emb, resp_emb).item()
        sim_exp = util.cos_sim(exp_emb, resp_emb).item()
        best_sim = max(sim_full, sim_exp)
        if best_sim >= threshold:
            matched_experience.append(responsibilities[i])

    missing_experience = list(set(responsibilities) - set(matched_experience))
    score = round(len(matched_experience) / len(responsibilities) * 100, 2) if responsibilities else 0

    return {
        "score": score,
        "matched_experience": matched_experience,
        "missing_experience": missing_experience
    }

def skill_scorer(resume, job_des):
    technical_skills = resume.get("skills", {}).get("technical_skills", [])
    soft_skills = resume.get("skills", {}).get("soft_skills", [])
    resume_skills = technical_skills + soft_skills
    requirements = job_des.get("requirements", [])

    resume_embeddings = model.encode(resume_skills, convert_to_tensor=True)
    job_embeddings = model.encode(requirements, convert_to_tensor=True)

    matched_skills = set()
    used_indexes = set()
    threshold = 0.7

    for i, job_emb in enumerate(job_embeddings):
        for j, skill_emb in enumerate(resume_embeddings):
            if j in used_indexes:
                continue
            sim_score = util.cos_sim(job_emb, skill_emb).item()
            if sim_score >= threshold:
                matched_skills.add(requirements[i])
                used_indexes.add(j)
                break

    missing_skills = list(set(requirements) - set(matched_skills))
    score = round(len(matched_skills) / len(requirements) * 100, 2) if requirements else 0

    return {
        "score": score,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills
    }

def evaluator(resume, job_des):
    skill_score = skill_scorer(resume, job_des)
    experience_score = experience_scorer(resume, job_des)

    final_score = round(
        (0.5 * experience_score['score']) +
        (0.5 * skill_score['score']), 2
    )

    return {
        "final_score": final_score,
        "components": {
            "skill_match_score": skill_score['score'],
            "experience_match_score" : experience_score['score']
        },
        "skills": skill_score,
        "experience": experience_score,
    }