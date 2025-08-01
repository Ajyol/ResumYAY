import requests
import json
import re
from typing import Dict, Any


class JobDescriptionParser:
    def __init__(self, ollama_url: str = "http://localhost:11434", model: str = "llama3.2:3b"):
        self.ollama_url = ollama_url
        self.model = model

    def create_parsing_prompt(self, job_description: str) -> str:
        """Create the AI prompt for job description parsing"""
        return f"""
You are an expert job description parser. Analyze this job description text and extract ALL relevant information. Read carefully and categorize everything properly.

JOB DESCRIPTION TEXT:
{job_description}

Extract information and return ONLY a valid JSON object in this exact format:

{{
    "job_info": {{
        "title": "",
        "company": "",
        "location": "",
        "employment_type": "",
        "experience_level": "",
        "salary_range": "",
        "remote_option": ""
    }},
    "job_summary": "",
    "responsibilities": [
        "responsibility 1",
        "responsibility 2"
    ],
    "requirements": {{
        "required_skills": [],
        "preferred_skills": [],
        "education": [],
        "experience_years": "",
        "certifications": []
    }},
    "technical_skills": {{
        "programming_languages": [],
        "frameworks_libraries": [],
        "tools_technologies": [],
        "databases": [],
        "cloud_platforms": [],
        "other_technical": []
    }},
    "soft_skills": [],
    "benefits": [],
    "company_info": {{
        "about_company": "",
        "company_size": "",
        "industry": ""
    }}
}}

EXTRACTION GUIDELINES:
... [prompt continues as-is with guidelines]
"""

    def parse_with_ai(self, job_description: str) -> Dict[str, Any]:
        """Parse job description using AI"""
        prompt = self.create_parsing_prompt(job_description)

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
                timeout=180
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

            return self.post_process_data(parsed_data)

        except requests.exceptions.RequestException as e:
            raise ValueError(f"Failed to connect to Ollama: {e}")

    def extract_json_from_response(self, ai_response: str) -> Dict[str, Any]:
        """Extract JSON from AI response"""
        json_str = None

        json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
        if json_match:
            json_str = json_match.group()

        if not json_str:
            code_block_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', ai_response, re.DOTALL)
            if code_block_match:
                json_str = code_block_match.group(1)

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
        """Clean up the parsed data"""
        if "responsibilities" in data and isinstance(data["responsibilities"], list):
            cleaned = [
                re.sub(r'^[-•–—*]\s*', '', item.strip())
                for item in data["responsibilities"]
                if isinstance(item, str) and item.strip()
            ]
            data["responsibilities"] = cleaned

        return self.ensure_structure(data)

    def ensure_structure(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure complete JSON structure"""
        template = {
            "job_info": {
                "title": "",
                "company": "",
                "location": "",
                "employment_type": "",
                "experience_level": "",
                "salary_range": "",
                "remote_option": ""
            },
            "job_summary": "",
            "responsibilities": [],
            "requirements": {
                "required_skills": [],
                "preferred_skills": [],
                "education": [],
                "experience_years": "",
                "certifications": []
            },
            "technical_skills": {
                "programming_languages": [],
                "frameworks_libraries": [],
                "tools_technologies": [],
                "databases": [],
                "cloud_platforms": [],
                "other_technical": []
            },
            "soft_skills": [],
            "benefits": [],
            "company_info": {
                "about_company": "",
                "company_size": "",
                "industry": ""
            }
        }

        def merge(template_dict, actual_dict):
            merged = template_dict.copy()
            if isinstance(actual_dict, dict):
                for key, value in actual_dict.items():
                    if key in merged:
                        if isinstance(merged[key], dict) and isinstance(value, dict):
                            merged[key] = merge(merged[key], value)
                        else:
                            merged[key] = value
            return merged

        return merge(template, data)

    def parse_job_description(self, job_description: str) -> Dict[str, Any]:
        """Main parsing function"""
        if len(job_description.strip()) < 50:
            raise ValueError("Job description is too short")
        return self.parse_with_ai(job_description)


# API for external use
def job_parser_from_text(job_description_text: str) -> Dict[str, Any]:
    parser = JobDescriptionParser()
    return parser.parse_job_description(job_description_text)


def job_parser_from_file(file_path: str) -> Dict[str, Any]:
    with open(file_path, 'r', encoding='utf-8') as f:
        return job_parser_from_text(f.read())
