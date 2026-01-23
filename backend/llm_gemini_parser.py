"""
Gemini API-based resume parser with structured output.
Simplified schema without nested models for better compatibility.
"""

import json
import os
import time
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from google import genai
from google.api_core.exceptions import ResourceExhausted, ServiceUnavailable

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()


# ✅ Simplified Schema (no complex nesting)

class ResumeData(BaseModel):
    name: str = Field(description="Full name of the candidate")
    email: str = Field(default="", description="Email address")
    phone: str = Field(default="", description="Phone number")
    linkedin: str = Field(default="", description="LinkedIn profile URL")
    github: str = Field(default="", description="GitHub profile URL")
    leetcode: str = Field(default="", description="LeetCode profile URL")
    website: str = Field(default="", description="Personal website URL")
    skills: List[str] = Field(default_factory=list, description="List of technical skills")
    projects: List[Dict[str, Any]] = Field(default_factory=list, description="List of projects with title, description, technologies, repo")
    experience: List[Dict[str, Any]] = Field(default_factory=list, description="List of work experiences")
    research: List[Dict[str, Any]] = Field(default_factory=list, description="List of research papers")
    education: List[Dict[str, Any]] = Field(default_factory=list, description="List of education entries")
    extracurriculars: List[str] = Field(default_factory=list, description="Extracurricular activities")


# ✅ Gemini API with retry logic

def call_gemini_with_retry(client, model: str, prompt: str, max_retries: int = 5):
    """
    Handles 503 UNAVAILABLE + 429 rate limits with exponential backoff.
    Uses JSON mode without strict schema to avoid validation errors.
    """
    delay = 2  # seconds

    for attempt in range(1, max_retries + 1):
        try:
            # Use JSON mode without strict schema
            return client.models.generate_content(
                model=model,
                contents=prompt,
                config={
                    "response_mime_type": "application/json",
                },
            )

        except (ResourceExhausted, ServiceUnavailable) as e:
            print(f"⚠️ Gemini overload attempt {attempt}/{max_retries}: {e}")
            
            if attempt == max_retries:
                raise e

            time.sleep(delay)
            delay *= 2  # exponential backoff

        except Exception as e:
            print(f"❌ Unexpected Gemini error: {e}")
            raise e


# ✅ Main Parsing Function

def parse_resume_gemini(resume_text: str, api_key: str = None) -> dict:
    """
    Parse resume using Gemini API with JSON output.
    
    Args:
        resume_text: Raw text extracted from PDF
        api_key: Optional Gemini API key (falls back to env var)
    
    Returns:
        dict: Structured resume data
    """
    
    if api_key is None:
        api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        raise ValueError(
            "Gemini API key not found. Set GEMINI_API_KEY environment variable or pass api_key parameter."
        )
    
    # Initialize Gemini client
    client = genai.Client(api_key=api_key)
    
    # ✅ Detailed prompt with clear JSON structure
    prompt = f"""
You are an expert resume parser. Extract structured information from the following resume text.

Return ONLY valid JSON in this EXACT format (no markdown, no explanations):

{{
  "name": "Full Name",
  "email": "email@example.com",
  "phone": "+1234567890",
  "linkedin": "https://linkedin.com/in/username",
  "github": "https://github.com/username",
  "leetcode": "https://leetcode.com/username",
  "website": "https://example.com",
  "skills": ["Python", "JavaScript", "React"],
  "projects": [
    {{
      "title": "Project Name",
      "description": ["Bullet point 1", "Bullet point 2"],
      "technologies": ["Tech1", "Tech2"],
      "repo": "https://github.com/user/repo"
    }}
  ],
  "experience": [
    {{
      "company": "Company Name",
      "role": "Role Title",
      "from": "Jan 2024",
      "to": "Present",
      "description": ["Responsibility 1", "Responsibility 2"],
      "skills": ["Skill1", "Skill2"]
    }}
  ],
  "research": [
    {{
      "title": "Paper Title",
      "description": ["Paper description"],
      "publication": "Journal/Conference Name"
    }}
  ],
  "education": [
    {{
      "degree": "Bachelor of Science",
      "institution": "University Name",
      "year": "2020-2024",
      "gpa": "3.8/4.0"
    }}
  ],
  "extracurriculars": ["Activity 1", "Activity 2"]
}}

CRITICAL RULES:
- Extract ALL projects, experience, education, and skills from the text
- DO NOT invent or hallucinate data not in the resume
- If a field is missing, use empty string "" or empty array []
- description fields MUST be arrays of strings (bullet points)
- Research papers go in "research", NOT "projects"
- Work experience (jobs/internships) go in "experience", NOT "projects"
- Personal/academic coding projects go in "projects"
- Preserve dates exactly as written
- Extract technologies/skills mentioned in project descriptions

Resume Text:
{resume_text}
"""
    
    try:
        # Generate response with retry logic
        response = call_gemini_with_retry(
            client,
            model="gemini-2.0-flash-exp",
            prompt=prompt,
            max_retries=5
        )
        
        print("===== RAW GEMINI OUTPUT =====")
        print(response.text[:500])
        print("=============================\n")
        
        # Parse JSON
        raw_data = json.loads(response.text)
        
        # Validate with Pydantic (lenient)
        validated = ResumeData(**raw_data)
        
        print(f"✅ Gemini parsed successfully:")
        print(f"   - Name: {validated.name}")
        print(f"   - Projects: {len(validated.projects)}")
        print(f"   - Experience: {len(validated.experience)}")
        print(f"   - Research: {len(validated.research)}")
        print(f"   - Skills: {len(validated.skills)}")
        
        # Convert to dict and restructure links
        result = validated.model_dump()
        
        # Restructure links to match expected format
        result["links"] = {
            "github": result.pop("github", ""),
            "linkedin": result.pop("linkedin", ""),
            "leetcode": result.pop("leetcode", ""),
            "website": result.pop("website", ""),
            "custom": []
        }
        
        return result
    
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing error: {e}")
        print(f"Raw output:\n{response.text}")
        raise
    
    except Exception as e:
        print(f"❌ Gemini API error: {e}")
        raise


# ✅ Standalone Test Function

def test_gemini_parser():
    """Test Gemini parser with sample resume text."""
    
    sample_resume = """
RAKSHAK S BARKUR
rakshakbarkur@gmail.com | +91-9148422805
LinkedIn: linkedin.com/in/rakshak05 | GitHub: github.com/Rakshak05

SKILLS
Python, FastAPI, React, Machine Learning, LLMs, PostgreSQL

PROJECTS & PUBLICATIONS

Resume to Portfolio
• Built a system using FastAPI and LLMs
• Automatically generates portfolios from PDF resumes
• Technologies: Python, FastAPI, Gemini API

Wonder Education Platform
• Developed an AI-powered learning companion
• Uses ML to detect student misunderstandings
• Technologies: React, Next.js, TensorFlow

EXPERIENCE

Software Intern | Tech Corp
Jan 2024 - Present
• Developed REST APIs using FastAPI
• Integrated machine learning models
• Skills: Python, FastAPI, Docker

EDUCATION

Bachelor of Engineering in Computer Science
XYZ University
2020 - 2024 | GPA: 8.5/10
"""
    
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("⚠️ GEMINI_API_KEY not set. Set it in your environment or .env file")
            return
        
        print("Testing Gemini parser...\n")
        result = parse_resume_gemini(sample_resume, api_key)
        
        print("\n===== PARSED RESULT =====")
        print(json.dumps(result, indent=2))
        print("=========================")
        
        return result
    
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_gemini_parser()
