import pdfplumber
import re


def extract_text_from_pdf(file):
    """Extract all text AND hyperlinks from a PDF file."""
    import io
    text = ""
    hyperlinks = []
    
    # First, try to extract hyperlinks using PyPDF2 (better for LaTeX PDFs)
    try:
        from PyPDF2 import PdfReader
        
        # Reset file pointer
        file.seek(0)
        pdf_reader = PdfReader(file)
        
        for page in pdf_reader.pages:
            # Try to extract annotations
            if '/Annots' in page:
                annotations = page['/Annots']
                for annot in annotations:
                    annot_obj = annot.get_object()
                    if annot_obj.get('/Subtype') == '/Link':
                        if '/A' in annot_obj:
                            action = annot_obj['/A']
                            if '/URI' in action:
                                uri = action['/URI']
                                hyperlinks.append(uri)
                                print(f"DEBUG PyPDF2: Found link: {uri}")
    except Exception as e:
        print(f"DEBUG PyPDF2: Could not extract links: {e}")
    
    # Reset file pointer for pdfplumber
    file.seek(0)
    
    # Extract text using pdfplumber
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    
    # Add extracted hyperlinks to the text so they can be found
    if hyperlinks:
        text += "\n\n" + "\n".join(hyperlinks)
        print(f"DEBUG: Added {len(hyperlinks)} hyperlinks to text")
    
    # Debug output
    print(f"DEBUG PDF: Text length = {len(text)}")
    print(f"DEBUG PDF: Contains 'http' = {'http' in text.lower()}")
    
    return text


def normalize_text(text):
    """Clean PDF text while PRESERVING line structure."""
    # Remove PDF CID garbage
    text = re.sub(r"\(cid:\d+\)", " ", text)

    # Normalize spaces BUT KEEP newlines
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n\n", text)

    return text.strip()


def extract_name(text):
    """Extract name from resume - works with ALL CAPS, Title Case, or mixed."""
    lines = text.split("\n")

    for line in lines[:8]:
        line = line.strip()

        # Remove obvious non-name words
        if any(w in line.lower() for w in ["email", "contact", "phone", "@"]):
            continue

        clean = re.sub(r"[^A-Za-z\s]", "", line).strip()

        if 2 <= len(clean.split()) <= 5:
            return clean.title()

    return "Candidate"


def extract_email(text):
    """Extract email address using regex."""
    email = re.search(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", text)
    return email.group(0) if email else ""


def extract_phone(text):
    """Extract 10-digit phone number."""
    phone = re.search(r"\b\d{10}\b", text)
    return phone.group(0) if phone else ""


def extract_skills(text):
    """Extract skills by matching against a known vocabulary.
    
    This is deliberately simple - accuracy first, sophistication later.
    """
    KNOWN_SKILLS = [
        "Python", "C", "C++", "Java", "Kotlin", "JavaScript",
        "HTML", "CSS", "MongoDB", "SQL",
        "TensorFlow", "PyTorch", "Scikit-Learn",
        "Pandas", "NumPy", "Matplotlib",
        "React", "Nest.js", "FastAPI",
        "Firebase", "Git", "Docker",
        "Machine Learning", "Deep Learning",
        "LLM", "NLP"
    ]

    found = set()
    text_lower = text.lower()

    for skill in KNOWN_SKILLS:
        if skill.lower() in text_lower:
            found.add(skill)

    return sorted(found)


def extract_projects(text):
    """Extract projects using line-by-line analysis - truly generic."""
    projects = []

    text_upper = text.upper()

    # 1️⃣ Locate PROJECTS section
    start = -1
    for k in ["PROJECTS", "TECHNICAL PROJECTS", "ACADEMIC PROJECTS"]:
        idx = text_upper.find(k)
        if idx != -1:
            start = idx + len(k)
            print(f"DEBUG: Found '{k}' at index {idx}")
            break

    if start == -1:
        print("DEBUG: No PROJECTS section found")
        return projects

    # 2️⃣ Find section end
    end = len(text)
    for k in ["EXPERIENCE", "EDUCATION", "SKILLS", "CERTIFICATIONS", "PUBLICATIONS"]:
        idx = text_upper.find(k, start)
        if idx != -1:
            end = idx
            print(f"DEBUG: Section ends at '{k}' (index {idx})")
            break

    section = text[start:end].strip()
    print(f"DEBUG: Extracted section ({len(section)} chars)")

    lines = [l.strip() for l in section.split("\n") if l.strip()]
    print(f"DEBUG: Processing {len(lines)} lines")

    current = None

    for i, line in enumerate(lines):
        # Bullet detection
        is_bullet = bool(re.match(r'^[•\-\*●○–]', line))

        # Heuristic: TITLE line
        looks_like_title = (
            not is_bullet
            and len(line) < 120
            and not line.endswith(".")
            and not re.search(r'\b(using|with|built|developed|designed)\b', line, re.I)
        )

        if looks_like_title:
            # Save previous project
            if current:
                projects.append(current)
                print(f"DEBUG: Saved project '{current['title']}'")

            current = {
                "title": line,
                "description": "",
                "repo": ""
            }
            print(f"DEBUG: Started new project: '{line}'")
        else:
            if not current:
                continue

            # Clean bullet symbols
            clean = re.sub(r'^[•\-\*●○–]\s*', '', line)

            current["description"] += clean + " "

    # Append last project
    if current:
        projects.append(current)
        print(f"DEBUG: Saved last project '{current['title']}'")

    # 3️⃣ Post-process projects
    final_projects = []

    for p in projects:
        desc = p["description"].strip()

        # Extract GitHub repo per project
        repo_match = re.search(r'https?://github\.com/[^\s,)\]]+', desc)
        if repo_match:
            p["repo"] = repo_match.group(0)

        # Cleanup title noise
        title = p["title"]
        title = re.sub(r'\s*\|\s*.*$', '', title)   # Remove tech stack
        title = re.sub(r'\s*[-–]\s*\d{4}.*$', '', title)
        title = title.strip()

        if len(title) < 3:
            print(f"DEBUG: Skipped short title: '{title}'")
            continue

        print(f"DEBUG: Final project: '{title}' ({len(desc)} chars)")

        final_projects.append({
            "title": title,
            "description": desc,
            "repo": p["repo"]
        })

    print(f"DEBUG: Extracted {len(final_projects)} projects total")
    return final_projects


def extract_links(text):
    """Extract links with username inference - works for resumes without full URLs."""
    links = {
        "github": "",
        "linkedin": "",
        "leetcode": "",
        "website": "",
        "custom": []
    }

    # 1. Explicit URLs
    urls = re.findall(r'https?://[^\s\)\],]+', text)
    for url in urls:
        u = url.lower()
        if "github.com" in u and not links["github"]:
            links["github"] = url
        elif "linkedin.com" in u and not links["linkedin"]:
            links["linkedin"] = url
        elif "leetcode.com" in u and not links["leetcode"]:
            links["leetcode"] = url
        else:
            domain_match = re.search(r'https?://(?:www\.)?([^/]+)', url)
            label = domain_match.group(1) if domain_match else "Link"
            links["custom"].append({"label": label, "url": url})

    # 2. Username inference (IMPORTANT FOR RESUMES WITHOUT FULL URLS)
    github = re.search(r'GitHub[:\s]*([A-Za-z0-9-]{3,})', text, re.IGNORECASE)
    if github and not links["github"]:
        links["github"] = f"https://github.com/{github.group(1)}"

    leetcode = re.search(r'LeetCode[:\s]*([A-Za-z0-9-_]{3,})', text, re.IGNORECASE)
    if leetcode and not links["leetcode"]:
        links["leetcode"] = f"https://leetcode.com/{leetcode.group(1)}"

    linkedin = re.search(r'LinkedIn[:\s]*([A-Za-z0-9-]{3,})', text, re.IGNORECASE)
    if linkedin and not links["linkedin"]:
        links["linkedin"] = f"https://linkedin.com/in/{linkedin.group(1)}"

    print(f"DEBUG: Extracted links = {links}")
    
    return links


def parse_resume(text):
    """Parse resume text and extract structured data.
    
    Returns:
        dict: Dictionary containing name, email, phone, skills, projects, and links
    """
    # Normalize text first
    text = normalize_text(text)
    
    # Debug: Show normalized text sample
    print(f"DEBUG NORMALIZED TEXT SAMPLE: {text[:500]}")
    
    return {
        "name": extract_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "skills": extract_skills(text),
        "projects": extract_projects(text),
        "links": extract_links(text)
    }