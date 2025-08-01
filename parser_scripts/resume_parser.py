import requests
import json
import re
import PyPDF2
import sys
from typing import Dict, Any

class ResumeParser:
    def __init__(self, ollama_url: str = "http://localhost:11434", model: str = "llama3.2:3b"):
        self.ollama_url = ollama_url
        self.model = model
        
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF file"""
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()
    
    def create_parsing_prompt(self, resume_text: str) -> str:
        """Create the AI prompt for resume parsing"""
        return f"""
You are an expert resume parser. Your job is to carefully read through this resume text and extract ALL information present. Read EVERY word carefully and don't miss anything.

RESUME TEXT TO ANALYZE:
{resume_text}

Extract information and return ONLY a valid JSON object in this exact format:

{{
    "personal_info": {{
        "name": "",
        "email": "",
        "phone": "",
        "location": "",
        "linkedin": "",
        "github": "",
        "portfolio": ""
    }},
    "professional_summary": "",
    "skills": {{
        "programming_languages": [],
        "frameworks_libraries": [],
        "tools_technologies": [],
        "databases": [],
        "other_technical_skills": []
    }},
    "experience": [
        {{
            "job_title": "",
            "company": "",
            "location": "",
            "start_date": "",
            "end_date": "",
            "responsibilities": [],
            "achievements": []
        }}
    ],
    "education": [
        {{
            "degree": "",
            "field": "",
            "institution": "",
            "location": "",
            "graduation_date": "",
            "gpa": ""
        }}
    ],
    "projects": [
        {{
            "name": "",
            "description": "",
            "technologies": [],
            "github_link": "",
            "live_demo": ""
        }}
    ],
    "certifications": [
        {{
            "name": "",
            "issuer": "",
            "date": ""
        }}
    ],
    "honors_achievements": [
        {{
            "title": "",
            "description": "",
            "date": "",
            "issuer": ""
        }}
    ]
}}

DETAILED EXTRACTION INSTRUCTIONS:

PERSONAL INFORMATION - Look for:
- Full name (usually at the top, might be in large font)
- Email address (contains @ symbol)
- Phone number (any format with numbers, parentheses, dashes)
- Address/Location (city, state, zip code)
- LinkedIn profile (linkedin.com/in/username or just username)
- GitHub profile (github.com/username or just username)
- Portfolio website or personal website

SKILLS - Categorize carefully:
Programming Languages: Python, Java, JavaScript, C++, C#, Go, Ruby, PHP, Swift, Kotlin, Scala, R, MATLAB, etc.
Frameworks/Libraries: React, Angular, Vue.js, Django, Flask, Spring Boot, Express.js, Node.js, Bootstrap, jQuery, TensorFlow, PyTorch, etc.
Tools/Technologies: Git, Docker, Kubernetes, Jenkins, AWS, Azure, Google Cloud, VS Code, IntelliJ, Eclipse, JIRA, etc.
Databases: MySQL, PostgreSQL, MongoDB, Redis, Oracle, SQL Server, SQLite, etc.
Other Technical Skills: Machine Learning, Data Science, DevOps, Agile, Scrum, etc.

EXPERIENCE - For each job:
- Job title exactly as written
- Company name
- Location (city, state)
- Start date and end date (if current job, note "Present")
- Bullet points describing responsibilities
- Any achievements or accomplishments mentioned

EDUCATION - For each degree:
- Degree type (Bachelor's, Master's, PhD, etc.)
- Field of study/Major
- School/University name
- Location of school
- Graduation date or date range
- GPA if mentioned

PROJECTS - Look for:
- Project names
- Project descriptions
- Technologies/languages used
- GitHub links or demo links
- Both personal and professional projects

CERTIFICATIONS - Find:
- Certificate names
- Issuing organization
- Date received or expiration date

AWARDS/HONORS - Extract:
- Award names
- Descriptions
- Dates received
- Issuing organization

CRITICAL RULES:
1. READ EVERY SINGLE WORD in the resume text
2. Don't skip any sections - look everywhere for information
3. Extract information EXACTLY as written - don't paraphrase
4. If you're unsure about categorization, include it rather than exclude it
5. Look for information that might be formatted differently (headers, footers, sidebars)
6. Pay attention to bullet points, lists, and formatted sections
7. Extract ALL responsibilities and achievements, not just the first few
8. Include ALL skills mentioned, even if they seem minor
9. Return ONLY the JSON object, no explanation or additional text

Be extremely thorough and don't miss any information!"""

    def parse_with_ai(self, resume_text: str) -> Dict[str, Any]:
        """Parse resume text using AI"""
        prompt = self.create_parsing_prompt(resume_text)
        
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.1,
                        "top_p": 0.9
                    }
                },
                timeout=200
            )
            
            if response.status_code != 200:
                raise ValueError(f"HTTP {response.status_code}: {response.text}")
            
            result = response.json()
            ai_response = result.get("response", "")
            
            if not ai_response.strip():
                raise ValueError("Empty response from AI")
            
            parsed_data = self.extract_json_from_response(ai_response)
            
            if not parsed_data:
                raise ValueError("Failed to extract valid JSON from AI response")
            
            parsed_data = self.post_process_data(parsed_data)
            return parsed_data
                
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Failed to connect to Ollama: {e}")
    
    def extract_json_from_response(self, ai_response: str) -> Dict[str, Any]:
        """Extract JSON from AI response using multiple methods"""
        json_str = None
        
        # Method 1: Direct JSON match
        json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
        if json_match:
            json_str = json_match.group()
        
        # Method 2: JSON in code blocks
        if not json_str:
            code_block_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', ai_response, re.DOTALL)
            if code_block_match:
                json_str = code_block_match.group(1)
        
        # Method 3: Clean and extract
        if not json_str:
            cleaned = re.sub(r'```json|```', '', ai_response).strip()
            start_idx = cleaned.find('{')
            end_idx = cleaned.rfind('}')
            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                json_str = cleaned[start_idx:end_idx + 1]
        
        if json_str:
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                pass
                
        return None
    
    def post_process_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean up and enhance the parsed data"""
        
        # Clean up personal info
        personal_info = data.get("personal_info", {})
        
        # Fix phone numbers
        if personal_info.get("phone"):
            phone = personal_info["phone"]
            digits = re.sub(r'\D', '', phone)
            if len(digits) == 10:
                personal_info["phone"] = f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
        
        # Clean URLs
        for url_field in ['linkedin', 'github', 'portfolio']:
            if personal_info.get(url_field):
                url = personal_info[url_field].strip()
                if url_field == 'linkedin' and not url.startswith('http') and 'linkedin.com' not in url:
                    personal_info[url_field] = f"linkedin.com/in/{url}"
                elif url_field == 'github' and not url.startswith('http') and 'github.com' not in url:
                    personal_info[url_field] = f"github.com/{url}"
        
        # Clean job titles
        if "experience" in data:
            for exp in data["experience"]:
                if exp.get("job_title"):
                    job_title = exp["job_title"]
                    job_title = re.sub(r'[\[\]\(\)]', '', job_title).strip()
                    exp["job_title"] = job_title
        
        # Ensure all required fields exist
        data = self.ensure_structure(data)
        
        return data
    
    def ensure_structure(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure the data has the complete expected structure"""
        template = {
            "personal_info": {
                "name": "",
                "email": "",
                "phone": "",
                "location": "",
                "linkedin": "",
                "github": "",
                "portfolio": ""
            },
            "professional_summary": "",
            "skills": {
                "programming_languages": [],
                "frameworks_libraries": [],
                "tools_technologies": [],
                "databases": [],
                "other_technical_skills": []
            },
            "experience": [],
            "education": [],
            "projects": [],
            "certifications": [],
            "honors_achievements": []
        }
        
        def merge_dicts(template_dict, actual_dict):
            result = template_dict.copy()
            if isinstance(actual_dict, dict):
                for key, value in actual_dict.items():
                    if key in result:
                        if isinstance(result[key], dict) and isinstance(value, dict):
                            result[key] = merge_dicts(result[key], value)
                        else:
                            result[key] = value
            return result
        
        return merge_dicts(template, data)
    
    def parse_resume(self, pdf_path: str) -> Dict[str, Any]:
        """Complete pipeline: PDF -> Text -> Parsed JSON"""
        resume_text = self.extract_text_from_pdf(pdf_path)
        
        if len(resume_text.strip()) < 50:
            raise ValueError("Extracted text is too short. PDF might be image-based or corrupted.")
        
        parsed_data = self.parse_with_ai(resume_text)
        return parsed_data

def main():
    if len(sys.argv) != 2:
        print("Usage: python resume_parser.py <pdf_file>")
        sys.exit(1)
    
    pdf_file = sys.argv[1]
    parser = ResumeParser()
    
    try:
        result = parser.parse_resume(pdf_file)
        
        # Create output filename
        output_file = pdf_file.replace('.pdf', '_parsed.json')
        
        # Save to JSON file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"Resume parsed successfully! Output saved to: {output_file}")
        
        # Print simple summary
        personal_info = result.get('personal_info', {})
        print(f"Name: {personal_info.get('name') or 'Not found'}")
        print(f"Email: {personal_info.get('email') or 'Not found'}")
        print(f"Phone: {personal_info.get('phone') or 'Not found'}")
        print(f"Location: {personal_info.get('location') or 'Not found'}")
        
        experience_count = len([exp for exp in result.get('experience', []) if exp.get('job_title')])
        education_count = len([edu for edu in result.get('education', []) if edu.get('degree')])
        projects_count = len([proj for proj in result.get('projects', []) if proj.get('name')])
        
        print(f"Experience entries: {experience_count}")
        print(f"Education entries: {education_count}")
        print(f"Projects: {projects_count}")
        
        skills = result.get('skills', {})
        total_skills = sum(len(v) for v in skills.values() if isinstance(v, list))
        print(f"Total skills extracted: {total_skills}")
        
    except Exception as e:
        print(f"Error: {e}")

def parse_resume_file(pdf_path: str) -> Dict[str, Any]:
    parser = ResumeParser()
    return parser.parse_resume(pdf_path)
