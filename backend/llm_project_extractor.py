import requests
import json
import re

OLLAMA_URL = "http://localhost:11434/api/generate"


def fix_json_errors(json_str: str) -> str:
    """Fix common JSON errors from LLM output."""
    # Remove trailing commas before closing braces/brackets
    json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)
    
    # Remove any markdown code blocks if present
    json_str = re.sub(r'^```json\s*', '', json_str, flags=re.MULTILINE)
    json_str = re.sub(r'^```\s*$', '', json_str, flags=re.MULTILINE)
    
    return json_str.strip()


def normalize_project_text(text: str) -> str:
    """Normalize project text to fix PDF extraction issues."""
    # Merge lines that start with lowercase (continuation lines)
    text = re.sub(r'\n(?=[a-z])', ' ', text)
    
    # Collapse multiple spaces
    text = re.sub(r'\s{2,}', ' ', text)
    
    # Clean up lines
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    normalized = []
    prev_was_bullet = False

    for line in lines:
        is_bullet = line.startswith(("•", "-", "*"))

        # Merge orphan headings into previous bullet block
        if not is_bullet and prev_was_bullet:
            normalized[-1] += " " + line
            prev_was_bullet = False
            continue

        normalized.append(line)
        prev_was_bullet = is_bullet

    return "\n".join(normalized)


def is_project_title(line: str) -> bool:
    """Strict title detection - prevents wrapped descriptions from being detected as titles."""
    line = line.strip()

    # Not a bullet
    if line.startswith(("•", "-", "*")):
        return False

    # Reject very long lines (likely descriptions)
    if len(line) > 80:
        return False

    # Reject lines with action verbs (likely descriptions)
    if re.search(r'\b(built|developed|implemented|designed|created|published|evaluated|integrated|leveraging|aiding|focusing|experimenting|building)\b', line, re.I):
        return False

    # Must contain letters
    if not re.search(r'[A-Za-z]{3,}', line):
        return False

    return True


def extract_bullets(lines):
    """Bullet-safe, PDF-safe extractor."""
    bullets = []
    current = ""

    for line in lines:
        clean = line.strip()

        # New bullet
        if clean.startswith("•"):
            if current:
                bullets.append(current.strip())
            current = clean.lstrip("• ").strip()

        # Continuation of previous bullet
        elif current and clean:
            current += " " + clean

    if current:
        bullets.append(current.strip())

    return bullets


def parse_projects_regex_fallback(projects_text: str):
    """Regex-based fallback parser with proper bullet continuation."""
    lines = projects_text.split('\n')
    
    projects = []
    current = None
    current_lines = []

    for line in lines:
        # NEW PROJECT TITLE (strict detection now)
        if is_project_title(line):
            # Save previous project
            if current:
                current["description"] = extract_bullets(current_lines)
                projects.append(current)

            current = {
                "title": line.strip(),
                "repo": "",
                "description": []
            }
            current_lines = []

        # Collect ALL lines for current project (no strip checks)
        elif current:
            current_lines.append(line)

    # FLUSH LAST PROJECT
    if current:
        current["description"] = extract_bullets(current_lines)
        projects.append(current)
    
    return projects


def extract_projects_with_llm(full_text: str):
    """
    Extract projects, research, and experience sections and send to LLM.
    """

    # ✅ FIX 1: Detect PROJECTS or EXPERIENCE sections
    projects_match = re.search(r'PROJECTS(\s*&\s*PUBLICATIONS)?', full_text, re.IGNORECASE)
    experience_match = re.search(r'EXPERIENCE', full_text, re.IGNORECASE)
    
    if not projects_match and not experience_match:
        print("DEBUG LLM: No PROJECTS or EXPERIENCE section found")
        return {"projects": [], "research": [], "experience": []}

    # Find the earliest section start
    start_idx = float('inf')
    if projects_match:
        start_idx = min(start_idx, projects_match.start())
        print(f"DEBUG LLM: PROJECTS keyword index = {projects_match.start()}")
    if experience_match:
        start_idx = min(start_idx, experience_match.start())
        print(f"DEBUG LLM: EXPERIENCE keyword index = {experience_match.start()}")
    
    section_text = full_text[int(start_idx):]
    
    # ✅ STEP 2: Find section end (after both PROJECTS and EXPERIENCE)
    end_keywords = [
        "EDUCATION", "SKILLS",
        "CERTIFICATIONS", "ACHIEVEMENTS",
        "EXTRA", "AWARDS", "REFERENCES"
    ]

    end = len(section_text)
    for k in end_keywords:
        m = re.search(r"\n\s*" + k + r"\s*\n", section_text.upper()[10:])
        if m:
            end = min(end, 10 + m.start())
            print(f"DEBUG LLM: Found end keyword '{k}' at {10 + m.start()}")
            break

    combined_text = normalize_project_text(section_text[:end])

    # print(f"DEBUG LLM: Sending PROJECTS+EXPERIENCE sections ({len(combined_text)} chars)")
    # print("===== TEXT SENT TO LLM =====")
    # print(combined_text[:500])  # Show first 500 chars
    # print("====================================")


    # ✅ IMPROVED PROMPT: LLM as cleaner/enhancer, not parser
    prompt = f"""
You are given PRE-EXTRACTED resume content.

Your task:
- CLEAN and IMPROVE the descriptions
- Fix grammar and clarity
- Classify each item into ONE type: "project", "research", or "experience"

CRITICAL RULES:
- DO NOT remove any content
- DO NOT merge items
- DO NOT split items
- DO NOT invent data
- Return items in the SAME structure you received

Classification guide:
- "project" → software, apps, systems, tools, personal/academic projects
- "research" → papers, publications, book chapters, conference papers
- "experience" → internships, jobs, work experience (company-based roles)

Return JSON in this exact format:

{{
  "projects": [
    {{
      "title": "",
      "description": ["", ""],
      "repo": ""
    }}
  ],
  "research": [
    {{
      "title": "",
      "description": ["", ""]
    }}
  ],
  "experience": [
    {{
      "company": "",
      "role": "",
      "from": "",
      "to": "",
      "description": ["", ""],
      "skills": ["", ""]
    }}
  ]
}}

Rules:
- Research items must NEVER appear inside "projects"
- Internships and jobs go into "experience", not "projects"
- For experience: extract company, role, dates, responsibilities, and skills used
- Projects may have repos, research and experience must not
- Do not invent data
- Output ONLY JSON (no text before or after, no markdown)

TEXT:
{combined_text}
"""

    payload = {
        "model": "llama3",
        "prompt": prompt,
        "stream": False
    }

    try:
        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=180
        )
        response.raise_for_status()

        raw = response.json().get("response", "")

        print("\n===== RAW LLM PROJECT OUTPUT =====\n")
        print(raw)
        print("\n=================================\n")

        # ✅ FIX 3: Safely extract JSON (handles object format now)
        # Extract JSON safely even if model adds text
        json_match = re.search(r"\{.*\}", raw, re.DOTALL)

        if not json_match:
            print("ERROR LLM: No JSON object found")
            return {"projects": [], "research": [], "experience": []}

        try:
            # Clean the JSON string before parsing
            json_str = json_match.group(0)
            json_str = fix_json_errors(json_str)
            
            print("===== CLEANED JSON =====")
            print(json_str[:500])
            print("========================")
            
            result = json.loads(json_str)
            
            # Validate structure
            if not isinstance(result, dict):
                print("ERROR LLM: Response is not an object")
                return {"projects": [], "research": [], "experience": []}
            
            # ✅ NEW RULE: Keep project if it has title and description
            # Don't reject internships or single-bullet projects
            projects_raw = result.get("projects", [])
            research_raw = result.get("research", [])
            experience_raw = result.get("experience", [])  # Extract experience
            
            # Minimal validation - keep if has title and description
            projects_validated = [
                p for p in projects_raw
                if p.get("title") and p.get("description")
            ]
            
            research_validated = [
                r for r in research_raw
                if r.get("title") and r.get("description")
            ]
            
            # Validate experience - need company, role, and description
            experience_validated = [
                e for e in experience_raw
                if e.get("company") and e.get("role") and e.get("description")
            ]
            
            # ✅ FIX 3: Separate publications from projects automatically
            projects_clean = []
            publications = []
            
            for p in projects_validated:
                title = p["title"].lower()
                
                if any(x in title for x in [
                    "ieee", "transactions", "conference", "journal",
                    "published", "paper", "publication"
                ]):
                    publications.append(p)
                else:
                    projects_clean.append(p)
            
            # Merge with research from LLM
            all_research = research_validated + publications
            
            print(f"Extracted {len(projects_clean)} projects, {len(all_research)} research papers, and {len(experience_validated)} experiences")
            
            
            return {
                "projects": projects_clean,
                "research": all_research,
                "experience": experience_validated  # Return experience
            }
            
        except json.JSONDecodeError as e:
            print("ERROR LLM JSON:", e)
            return {"projects": [], "research": [], "experience": []}

    except Exception as e:
        print(f"ERROR LLM: {e}")
        return {"projects": [], "research": [], "experience": []}


def check_ollama_available():
    """Check if Ollama is running."""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        return response.status_code == 200
    except:
        return False
