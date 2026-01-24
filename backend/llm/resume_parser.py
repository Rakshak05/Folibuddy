"""
Resume parser - the main public API.
This is what everything else imports and uses.
"""

import json
from backend.utils.pdf_reader import extract_text_from_pdf
from backend.llm.gemini_client import call_gemini
from backend.llm.resume_schema import Resume


def parse_resume(pdf_path: str) -> dict:
    """
    Parse a resume PDF and extract structured data using Gemini API.
    
    This is the main entry point for resume parsing.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        Dictionary containing structured resume data with keys:
        - name, email, phone
        - linkedin, github, leetcode, website
        - skills (list)
        - projects (list of dicts)
        - experience (list of dicts)
        - research (list of dicts)
        - education (list of dicts)
        - extracurriculars (list)
        
    Raises:
        Exception: If parsing fails
    """
    
    # Step 1: Extract text from PDF
    print("📄 Extracting text from PDF...")
    resume_text = extract_text_from_pdf(pdf_path)
    print(f"✅ Extracted {len(resume_text)} characters")
    
    # Step 2: Build prompt for Gemini
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
    
    # Step 3: Call Gemini API
    print("🤖 Calling Gemini API...")
    raw_response = call_gemini(prompt)
    print("✅ Received response from Gemini")
    
    # Step 4: Parse and validate JSON
    print("🔍 Parsing and validating response...")
    try:
        raw_data = json.loads(raw_response)
        
        # Validate with Pydantic
        validated = Resume(**raw_data)
        
        # Convert to dict
        result = validated.model_dump()
        
        # Restructure links to match expected format
        result["links"] = {
            "github": result.pop("github", ""),
            "linkedin": result.pop("linkedin", ""),
            "leetcode": result.pop("leetcode", ""),
            "website": result.pop("website", ""),
            "custom": []
        }
        
        print(f"✅ Successfully parsed resume:")
        print(f"   - Name: {result['name']}")
        print(f"   - Projects: {len(result['projects'])}")
        print(f"   - Experience: {len(result['experience'])}")
        print(f"   - Research: {len(result['research'])}")
        print(f"   - Skills: {len(result['skills'])}")
        
        return result
        
    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse JSON response: {e}")
        print(f"Raw response: {raw_response[:500]}")
        raise
        
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        raise
