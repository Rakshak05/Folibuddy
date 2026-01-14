import requests
import json
import re


def extract_projects_with_llm(text, model="llama3.2"):
    """
    Use LLM ONLY for project extraction.
    This is the hybrid approach - regex for simple fields, LLM for complex structure.
    
    Args:
        text: Full resume text
        model: Ollama model to use
    
    Returns:
        list: Array of project dicts with title, description (string), repo
    """
    # 1. Extract PROJECTS section using simple string search
    text_upper = text.upper()
    
    start = -1
    for keyword in ["PROJECTS", "TECHNICAL PROJECTS", "ACADEMIC PROJECTS"]:
        idx = text_upper.find(keyword)
        if idx != -1:
            start = idx + len(keyword)
            print(f"DEBUG: Found '{keyword}' section at index {idx}")
            break
    
    if start == -1:
        print("DEBUG: No PROJECTS section found")
        return []
    
    # Find section end
    end = len(text)
    for keyword in ["EXPERIENCE", "EDUCATION", "SKILLS", "CERTIFICATIONS", "PUBLICATIONS"]:
        idx = text_upper.find(keyword, start)
        if idx != -1:
            end = idx
            break
    
    projects_section = text[start:end].strip()
    
    if len(projects_section) < 10:
        print("DEBUG: PROJECTS section too short")
        return []
    
    print(f"DEBUG: Extracted PROJECTS section ({len(projects_section)} chars)")
    print(f"DEBUG: Section content: {projects_section[:300]}...")
    
    # 2. Send ONLY projects section to LLM
    prompt = f"""Extract projects from the following resume section.

RULES:
- Each project is separate
- Title is the heading line (usually bold or capitalized)
- Description must be an array of bullet points or key achievements
- Extract GitHub repo URL if mentioned anywhere in the project
- Do not invent information
- Output valid JSON only, no markdown, no explanations

JSON FORMAT:
[
  {{
    "title": "",
    "description": ["", ""],
    "repo": ""
  }}
]

TEXT:
<<<
{projects_section}
>>>

Output the JSON array now:"""

    try:
        print(f"DEBUG LLM: Sending projects section to {model}...")
        
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "temperature": 0.1
            },
            timeout=60
        )
        
        if response.status_code != 200:
            print(f"ERROR LLM: Status {response.status_code}")
            return []
        
        result = response.json()
        llm_output = result.get("response", "").strip()
        
        print(f"DEBUG LLM: Received {len(llm_output)} chars")
        
        # Extract JSON from response
        json_match = re.search(r'\[.*\]', llm_output, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
        else:
            json_str = llm_output
        
        # Parse JSON
        projects = json.loads(json_str)
        
        if not isinstance(projects, list):
            print("ERROR LLM: Response is not an array")
            return []
        
        # Convert to UI format (description array -> string with bullets)
        final_projects = []
        for proj in projects:
            if not isinstance(proj, dict):
                continue
            
            title = proj.get("title", "").strip()
            desc_array = proj.get("description", [])
            repo = proj.get("repo", "").strip()
            
            # Convert description array to string
            if isinstance(desc_array, list):
                desc_text = "\n".join([f"• {point.strip()}" for point in desc_array if point.strip()])
            elif isinstance(desc_array, str):
                desc_text = desc_array
            else:
                desc_text = ""
            
            if title and len(title) >= 3:
                final_projects.append({
                    "title": title,
                    "description": desc_text,
                    "repo": repo
                })
        
        print(f"DEBUG LLM: Extracted {len(final_projects)} projects")
        return final_projects
    
    except requests.exceptions.Timeout:
        print("ERROR LLM: Request timed out")
        return []
    
    except requests.exceptions.ConnectionError:
        print("ERROR LLM: Cannot connect to Ollama - is it running?")
        return []
    
    except json.JSONDecodeError as e:
        print(f"ERROR LLM: Invalid JSON: {e}")
        print(f"LLM output was: {llm_output[:500]}")
        return []
    
    except Exception as e:
        print(f"ERROR LLM: Unexpected error: {e}")
        return []


def check_ollama_available():
    """Check if Ollama is running."""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        return response.status_code == 200
    except:
        return False
