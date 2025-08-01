from keybert import KeyBERT
import re
import json
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import PunktSentenceTokenizer

nltk.download('stopwords')
nltk.download('punkt')
nltk.download('punkt_tab')

stop_words = set(stopwords.words('english'))
model = KeyBERT(model='all-MiniLM-L12-v2')
tokenizer = PunktSentenceTokenizer()

def extract_sections(job_des):
    sections = {
        "responsibilities" : "",
        "requirements" : ""
    }
    job_des = job_des.lower()

    responsibilities = re.search(r"(responsibilities:)(.*?)(requirements:|$)", job_des, re.DOTALL)
    requirements = re.search(r"(requirements:)(.*)", job_des, re.DOTALL)

    if responsibilities:
        sections["responsibilities"] = responsibilities.group(2).strip()
    if requirements:
        sections["requirements"] = requirements.group(2).strip()

    return sections

def extract_keywords(txt, top_n = 10):
    if not txt.strip():
        return []
    keywords = model.extract_keywords(
        txt,
        keyphrase_ngram_range=(1, 2),
        stop_words='english',
        use_maxsum=True,
        top_n=top_n
    )
    return [kw[0] for kw in keywords]

def extract_sentences(txt):
    return [s.strip() for s in tokenizer.tokenize(txt) if s.strip()]

def job_parser(job_des):
    sections = extract_sections(job_des)
    responsibilities = extract_sentences(sections["responsibilities"])
    responsibilities_json = [
        s.lstrip("-•–—").strip().lower() for s in responsibilities
    ]
    skills = {
        "responsibilities" : responsibilities_json,
        "requirements" : extract_keywords(sections["requirements"], top_n=10)
    }
    return json.dumps(skills, indent=2)