import requests
import json
import re

OLLAMA_URL = "http://localhost:11434/api/generate"


def normalize_project_text(text: str) -> str:
    """Normalize project text to fix PDF extraction issues."""
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
    """Robust title detection - allows pipes, dates, institutions."""
    if len(line) < 8:
        return False

    # must not be a bullet
    if line.strip().startswith("•"):
        return False

    # contains letters, not all caps noise
    if not re.search(r'[a-zA-Z]{4,}', line):
        return False

    # allow | Supervisor, dates, institutions
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
        # NEW PROJECT TITLE
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

        # Collect lines for current project
        elif current and line.strip():
            current_lines.append(line)

    # FLUSH LAST PROJECT
    if current:
        current["description"] = extract_bullets(current_lines)
        projects.append(current)
    
    return projects


def extract_projects_with_llm(full_text: str):
    """
    Extract ONLY the projects section and send it to LLM.
    """

    # ✅ FIX 1: Detect section headers properly
    match = re.search(r'PROJECTS(\s*&\s*PUBLICATIONS)?', full_text, re.IGNORECASE)
    if not match:
        print("DEBUG LLM: No PROJECT section found")
        return {"projects": [], "research": []}

    start_idx = match.start()
    section_text = full_text[start_idx:]
    
    print(f"DEBUG LLM: PROJECT keyword index = {start_idx}")

    # ✅ STEP 2: Find section end with better keyword matching
    end_keywords = [
        "EDUCATION", "EXPERIENCE", "SKILLS",
        "CERTIFICATIONS", "ACHIEVEMENTS",
        "EXTRA", "AWARDS"
    ]

    end = len(section_text)
    for k in end_keywords:
        m = re.search(r"\n\s*" + k + r"\s*\n", section_text.upper()[10:])
        if m:
            end = min(end, 10 + m.start())
            print(f"DEBUG LLM: Found end keyword '{k}' at {10 + m.start()}")
            break

    projects_text = normalize_project_text(section_text[:end])

    print(f"DEBUG LLM: Sending PROJECTS section ({len(projects_text)} chars)")
    print("===== PROJECTS TEXT SENT TO LLM =====")
    print(projects_text[:500])  # Show first 500 chars
    print("====================================")


    # ✅ FIX 2: Make the prompt LLM-proof with projects/research split
    prompt = f"""
You are a resume parser.

Your task:
Extract ALL projects and research papers from the text.

You must classify each item into ONE of two types:
- "project" → software, apps, systems, tools, internships
- "research" → papers, publications, book chapters

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
  ]
}}

Rules:
- Research items must NEVER appear inside "projects"
- Projects may have repos, research must not
- Do not invent data
- Output ONLY JSON
- No text before or after
- No markdown

TEXT:
{projects_text}
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
            return {"projects": [], "research": []}

        try:
            result = json.loads(json_match.group(0))
            
            # Validate structure
            if not isinstance(result, dict):
                print("ERROR LLM: Response is not an object")
                return {"projects": [], "research": []}
            
            # ✅ NEW RULE: Keep project if it has title and description
            # Don't reject internships or single-bullet projects
            projects_raw = result.get("projects", [])
            research_raw = result.get("research", [])
            
            # Minimal validation - keep if has title and description
            projects_validated = [
                p for p in projects_raw
                if p.get("title") and p.get("description")
            ]
            
            research_validated = [
                r for r in research_raw
                if r.get("title") and r.get("description")
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
            
            print(f"✅ Extracted {len(projects_clean)} projects and {len(all_research)} research papers")
            
            return {
                "projects": projects_clean,
                "research": all_research
            }
            
        except json.JSONDecodeError as e:
            print("ERROR LLM JSON:", e)
            return {"projects": [], "research": []}

    except Exception as e:
        print(f"ERROR LLM: {e}")
        return []


def check_ollama_available():
    """Check if Ollama is running."""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        return response.status_code == 200
    except:
        return False
