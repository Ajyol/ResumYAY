#!/usr/bin/env python3

import requests
import json
import re
import sys
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

JOB INFO:
- Extract job title, company name, location
- Determine employment type (Full-time, Part-time, Contract, Internship)
- Identify experience level (Entry, Mid, Senior, Executive)
- Look for salary information
- Check for remote/hybrid options

RESPONSIBILITIES:
- Extract all job duties and responsibilities
- Look for sections like "What you'll do", "Responsibilities", "Day-to-day tasks"
- Clean up bullet points and format as clear sentences
- Include all tasks mentioned

REQUIREMENTS:
- required_skills: Must-have skills explicitly mentioned
- preferred_skills: Nice-to-have or preferred skills
- education: Degree requirements (Bachelor's, Master's, etc.)
- experience_years: Years of experience required
- certifications: Required or preferred certifications

TECHNICAL SKILLS - Categorize properly:
- programming_languages: Python, Java, JavaScript, C++, C#, HTML, CSS, etc.
- frameworks_libraries: React, Angular, Django, Spring, .NET, .NET Core, Entity Framework, etc.
- tools_technologies: Git, Docker, Jenkins, JIRA, Visual Studio, etc.
- databases: MySQL, PostgreSQL, MongoDB, SQL Server, etc.
- cloud_platforms: AWS, Azure, Google Cloud, Azure Active Directory, etc.
- other_technical: APIs, DevOps, Machine Learning, SaaS, etc.

CRITICAL: Do NOT put non-technical skills like "Bilingual" in technical_skills. Only include actual programming languages, frameworks, tools, databases, and cloud platforms.

SOFT SKILLS:
- Communication, leadership, teamwork, problem-solving, etc.

BENEFITS:
- Health insurance, 401k, vacation, remote work, etc.

COMPANY INFO:
- Extract any information about the company
- Company size, industry, mission, culture

IMPORTANT RULES:
1. Read the ENTIRE job description carefully
2. Look for information in different sections (it might not be clearly labeled)
3. Extract information exactly as written
4. If something is mentioned as "required" vs "preferred", categorize accordingly
5. Don't miss any technical skills or requirements
6. Include all responsibilities, not just the first few
7. Return ONLY the JSON object, no additional text

Be thorough and accurate!"""

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
            
            parsed_data = self.post_process_data(parsed_data)
            return parsed_data
                
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Failed to connect to Ollama: {e}")
    
    def extract_json_from_response(self, ai_response: str) -> Dict[str, Any]:
        """Extract JSON from AI response"""
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
        """Clean up the parsed data"""
        
        # Clean up responsibilities (remove bullet points, dashes)
        if "responsibilities" in data and isinstance(data["responsibilities"], list):
            cleaned_responsibilities = []
            for resp in data["responsibilities"]:
                if isinstance(resp, str):
                    # Remove common bullet point characters
                    cleaned = re.sub(r'^[-•–—*]\s*', '', resp.strip())
                    if cleaned:
                        cleaned_responsibilities.append(cleaned)
            data["responsibilities"] = cleaned_responsibilities
        
        # Ensure structure exists
        data = self.ensure_structure(data)
        
        return data
    
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
    
    def parse_job_description(self, job_description: str) -> Dict[str, Any]:
        """Main parsing function"""
        if len(job_description.strip()) < 50:
            raise ValueError("Job description is too short")
        
        parsed_data = self.parse_with_ai(job_description)
        return parsed_data

def parse_from_file(filename: str) -> str:
    """Parse job description from a text file"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            job_description = f.read()
        
        parser = JobDescriptionParser()
        result = parser.parse_job_description(job_description)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)

def parse_from_input() -> str:
    """Parse job description from user input"""
    print("=== Job Description Parser ===")
    print("Paste your job description below. Press Ctrl+D (Mac/Linux) or Ctrl+Z+Enter (Windows) when done:")
    print("-" * 50)
    
    try:
        # Read multi-line input
        lines = []
        while True:
            try:
                line = input()
                lines.append(line)
            except EOFError:
                break
        
        job_description = '\n'.join(lines)
        
        if not job_description.strip():
            return json.dumps({"error": "No job description provided"}, indent=2)
        
        print("\nParsing job description...")
        
        parser = JobDescriptionParser()
        result = parser.parse_job_description(job_description)
        return json.dumps(result, indent=2)
        
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)

def main():
    if len(sys.argv) > 1:
        # Parse from file
        filename = sys.argv[1]
        print(f"Parsing job description from file: {filename}")
        
        # Debug: Show what we're reading from the file
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                file_content = f.read()
            print(f"File content preview (first 200 chars):")
            print("-" * 50)
            print(file_content[:200] + "..." if len(file_content) > 200 else file_content)
            print("-" * 50)
        except Exception as e:
            print(f"Error reading file: {e}")
            return
        
        result = parse_from_file(filename)
        print(result)
        
        # Save output
        output_file = filename.replace('.txt', '_parsed.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(result)
        print(f"\nOutput saved to: {output_file}")
    else:
        # Interactive mode
        result = parse_from_input()
        print("\n" + "="*50)
        print("PARSED RESULT:")
        print("="*50)
        print(result)
        
        # Ask if user wants to save
        save = input("\nDo you want to save this to a file? (y/n): ")
        if save.lower() == 'y':
            filename = input("Enter filename (without extension): ") or "parsed_job"
            with open(f"{filename}.json", 'w', encoding='utf-8') as f:
                f.write(result)
            print(f"Saved to {filename}.json")

if __name__ == "__main__":
    main()