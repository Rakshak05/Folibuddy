import json
import re
from backend.llm_loader import pipe


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

def normalize_projects(data):
    """
    Ensures description is always List[str]
    """
    for project in data:
        desc = project.get("description", [])
        normalized = []

        for d in desc:
            if isinstance(d, dict) and "text" in d:
                normalized.append(d["text"])
            elif isinstance(d, str):
                normalized.append(d)

        project["description"] = normalized

    return data

def extract_projects_with_llm(text: str):
    """
    Extract projects ONLY from resume text.
    """

    # 1. Isolate PROJECTS section (cheap + reliable)
    upper = text.upper()
    start = upper.find("PROJECT")
    if start == -1:
        return []

    end = len(text)
    for k in ["EXPERIENCE", "EDUCATION", "SKILLS", "RESEARCH"]:
        i = upper.find(k, start + 10)
        if i != -1:
            end = min(end, i)

    projects_text = text[start:end].strip()

    # 2. STRICT prompt (no classification, no cleaning)
    prompt = f"""
Extract projects from the text below.

Return ONLY valid JSON in this format:
[
  {{
    "title": "Project title",
    "description": ["bullet point", "bullet point"]
  }}
]

Rules:
- Each project has ONE title
- Description MUST be a list of strings
- Do NOT add extra keys
- Do NOT add explanations
- Do NOT repeat content
- Do NOT invent data

Text:
{projects_text}
"""

    # 3. Run model
    output = pipe(
        prompt,
        max_new_tokens=512,
        do_sample=False
    )[0]["generated_text"]

    # 4. Extract JSON safely
    match = re.search(r"\[.*\]", output, re.S)
    if not match:
        print("LLM JSON not found")
        return []

    try:
        return json.loads(match.group())
    except Exception as e:
        print("JSON parse failed:", e)
        return []
