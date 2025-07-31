def parse_resume(file):
    """
    Mock resume parser.
    Returns a dict with the same structure your real parser produces.
    """
    return {
        "professional_summary": "Reduced hosting costs by 28% and boosted system reliability",
        "contact_information": {
            "email": "r.voss@email.com",
            "phone": None,
            "linkedin": None,
            "github": None,
            "name": "Riley Voss"
        },
        "skills": {
            "technical_skills": [
                "AWS", "Jenkins", "Oracle", "R", "React", "Spring", "TensorFlow"
            ],
            "soft_skills": [],
            "technical_count": 7,
            "soft_count": 0,
            "total_skills_count": 7
        },
        "education": [
            {
                "degree": "Bachelor of Science Software Engineering, California Institute of Technology",
                "institution": "California Institute of Technology",
                "year": "2006"
            }
        ],
        "experience": {
            "years": 0,
            "level": "Entry Level",
            "has_experience_section": True
        },
        "sections_present": {
            "contact_information": True,
            "professional_summary": True,
            "work_experience": True,
            "education": True,
            "skills": True,
            "projects": True,
            "certifications": False
        },
        "resume_metrics": {
            "word_count": 271,
            "character_count": 1874,
            "sentence_count": 4,
            "estimated_pages": 1,
            "average_words_per_sentence": 67.8
        },
        "summary": {
            "total_skills": 7,
            "technical_skills": 7,
            "soft_skills": 0,
            "education_entries": 1,
            "estimated_experience": 0,
            "word_count": 271,
            "readability_score": "Good"
        }
    }

