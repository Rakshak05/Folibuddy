import requests
import json
import re


PROMPT_TEMPLATE = """You are an expert resume parser.

Your task:
Read the resume text provided below and extract structured information.

STRICT RULES:
- Use ONLY information explicitly present in the resume
- DO NOT invent or assume anything
- DO NOT merge different projects
- A project may have multiple description points
- Output MUST be valid JSON
- Follow the schema EXACTLY
- No explanations, no markdown, no comments

JSON SCHEMA:
{
  "name": "",
  "email": "",
  "phone": "",
  "skills": [],
  "links": {
    "github": "",
    "linkedin": "",
    "leetcode": "",
    "website": "",
    "other": []
  },
  "projects": [
    {
      "title": "",
      "description": [],
      "repo": ""
    }
  ]
}

INSTRUCTIONS FOR PROJECTS:
- Each project must be a separate object
- Project title is usually a heading or bold line
- Description points come from bullets OR wrapped text
- If GitHub repository link is mentioned near a project, attach it to that project
- If no repo is mentioned, leave it empty

RESUME TEXT:
<<<
{RESUME_TEXT_HERE}
>>>

Output the JSON now:"""


def parse_resume_with_llm(resume_text, model="llama3.2"):
    """
    Parse resume using LLM - clean, reliable, no regex hell.
    
    Args:
        resume_text: Raw text extracted from PDF
        model: Ollama model to use (default: llama3.2)
    
    Returns:
        dict: Structured resume data following the schema
    """
    # Build prompt
    prompt = PROMPT_TEMPLATE.replace("{RESUME_TEXT_HERE}", resume_text)
    
    print(f"DEBUG LLM: Sending {len(resume_text)} chars to {model}...")
    
    try:
        # Call Ollama
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "temperature": 0.1  # Low temperature for consistent parsing
            },
            timeout=60
        )
        
        if response.status_code != 200:
            raise Exception(f"Ollama returned status {response.status_code}")
        
        result = response.json()
        llm_output = result.get("response", "").strip()
        
        print(f"DEBUG LLM: Received {len(llm_output)} chars")
        print(f"DEBUG LLM: Output sample: {llm_output[:200]}...")
        
        # Extract JSON from response (LLM might wrap it in markdown)
        json_match = re.search(r'\{.*\}', llm_output, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
        else:
            json_str = llm_output
        
        # Parse JSON
        parsed = json.loads(json_str)
        
        # Validate schema
        parsed = validate_and_fix_schema(parsed)
        
        print(f"DEBUG LLM: Successfully parsed resume")
        print(f"DEBUG LLM: Found {len(parsed.get('projects', []))} projects")
        print(f"DEBUG LLM: Found {len(parsed.get('skills', []))} skills")
        
        return parsed
    
    except requests.exceptions.Timeout:
        print("ERROR LLM: Request timed out - Ollama might be slow or hung")
        return get_fallback_structure()
    
    except requests.exceptions.ConnectionError:
        print("ERROR LLM: Cannot connect to Ollama - is it running?")
        return get_fallback_structure()
    
    except json.JSONDecodeError as e:
        print(f"ERROR LLM: Invalid JSON from LLM: {e}")
        print(f"LLM output was: {llm_output[:500]}")
        return get_fallback_structure()
    
    except Exception as e:
        print(f"ERROR LLM: Unexpected error: {e}")
        return get_fallback_structure()


def validate_and_fix_schema(data):
    """Ensure the parsed data matches our schema exactly."""
    
    # Ensure all required fields exist
    validated = {
        "name": data.get("name", "Candidate"),
        "email": data.get("email", ""),
        "phone": data.get("phone", ""),
        "skills": data.get("skills", []),
        "links": {
            "github": "",
            "linkedin": "",
            "leetcode": "",
            "website": "",
            "other": []
        },
        "projects": []
    }
    
    # Fix links structure
    if "links" in data and isinstance(data["links"], dict):
        validated["links"]["github"] = data["links"].get("github", "")
        validated["links"]["linkedin"] = data["links"].get("linkedin", "")
        validated["links"]["leetcode"] = data["links"].get("leetcode", "")
        validated["links"]["website"] = data["links"].get("website", "")
        validated["links"]["other"] = data["links"].get("other", [])
    
    # Fix projects structure
    if "projects" in data and isinstance(data["projects"], list):
        for proj in data["projects"]:
            if isinstance(proj, dict):
                # Ensure description is array
                desc = proj.get("description", [])
                if isinstance(desc, str):
                    desc = [desc]
                elif not isinstance(desc, list):
                    desc = []
                
                validated["projects"].append({
                    "title": proj.get("title", ""),
                    "description": desc,
                    "repo": proj.get("repo", "")
                })
    
    return validated


def get_fallback_structure():
    """Return minimal valid structure if LLM fails."""
    return {
        "name": "Candidate",
        "email": "",
        "phone": "",
        "skills": [],
        "links": {
            "github": "",
            "linkedin": "",
            "leetcode": "",
            "website": "",
            "other": []
        },
        "projects": []
    }


def check_ollama_available():
    """Check if Ollama is running and has the required model."""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code == 200:
            models = response.json().get("models", [])
            model_names = [m.get("name", "") for m in models]
            print(f"DEBUG LLM: Available models: {model_names}")
            return True
        return False
    except:
        return False
