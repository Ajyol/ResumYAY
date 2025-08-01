import spacy
from sentence_transformers import SentenceTransformer, util
from torch.ao.nn.quantized.functional import threshold

nlp = spacy.load("en_core_web_sm", disable = ["ner", "parser"])
model = SentenceTransformer("all-MiniLM-L12-v2")

def resume_experience(exp_list):
    exp = []
    for job in exp_list:
        header = f"{job['job_title']} at {job['company']} ({job['start_date']} - {job['end_date']})"
        exp.append(header)
        exp.extend(job["responsibilities"])
    return "\n".join(exp)

def resume_skills(skill_dict):
    skills = []
    for key in skill_dict:
        skills.extend(skill_dict[key])
    return list(set(skills))

def resume_projects(projects):
    des = []
    for proj in projects:
        tech = ", ".join(proj.get("technologies", []))
        des.append(f"{proj['name']}: {tech}")
    return "\n".join(des)

def exp_scorer(resume, job_des):
    work_exp = resume_experience(resume["experience"])
    projects = resume_projects(resume["projects"])
    experiences = work_exp + projects
    experience_embs = model.encode(experiences, convert_to_tensor=True)

    responsibilities = job_des.get("responsibilities", [])
    responsibilities_embs = model.encode(responsibilities, convert_to_tensor=True)

    matched = []
    for i, responsibilities_emb in enumerate(responsibilities_embs):
        sim = util.cos_sim(experience_embs, responsibilities_emb).item()
        if sim >= 0.70:
            matched.append(job_des[i])

    score = round(len(matched) / len(responsibilities) * 100, 2) if responsibilities else 0
    return {
        "score": score,
        "matched_experience": matched,
        "missing_experience": list(set(responsibilities) - set(matched))
    }

def skill_scorer(resume, job_des):
    skills = resume_skills(resume["skills"])
    skills_emb = model.encode(skills, convert_to_tensor=True)

    requirements = job_des["requirements"]["required_skills"]
    requirements_emb = model.encode(requirements, convert_to_tensor=True)

    matched = set()
    used = set()

    for i, requirement_emb in enumerate(requirements_emb):
        for j, skill_emb in enumerate(skills_emb):
            if j in used:
                continue
            sim = util.cos_sim(requirement_emb, skill_emb).item()
            if sim >= 0.70:
                matched.add(requirements[i])
                used.add(j)
                break

    score = round(len(matched) / len(requirements) * 100, 2) if requirements else 0
    return {
        "score": score,
        "matched_skills": list(matched),
        "missing_skills": list(set(requirements) - matched)
    }

def evaluator(resume, job_des):
    skill_score = skill_scorer(resume, job_des)
    exp_score = exp_scorer(resume, job_des)
    final_score = round(0.5 * skill_score['score'] + 0.5 * exp_score['score'], 2)
    return {
        "final_score": final_score,
        "components": {
            "skill_match_score": skill_score['score'],
            "experience_match_score": exp_score['score']
        },
        "skills": skill_score,
        "experience": exp_score,
    }