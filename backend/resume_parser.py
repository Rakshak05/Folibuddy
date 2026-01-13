import pdfplumber
import re

def extract_text_from_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text


def extract_skills(text):
    lines = text.split("\n")
    skills = set()
    in_skills = False

    skill_headers = {
        "SKILLS", "TECHNICAL SKILLS", "TECHNICAL EXPERTISE",
        "TOOLS", "TOOLS & TECHNOLOGIES"
    }

    stop_headers = {
        "PROJECTS", "EXPERIENCE", "EDUCATION",
        "CERTIFICATIONS", "ACHIEVEMENTS"
    }

    for line in lines:
        stripped = line.strip()

        if stripped.upper() in skill_headers:
            in_skills = True
            continue

        if in_skills and stripped.upper() in stop_headers:
            break

        if in_skills and stripped:
            stripped = stripped.replace("&", ",").replace("/", ",")
            for skill in stripped.split(","):
                skill = skill.strip()
                if len(skill) > 1:
                    skills.add(skill)

    return sorted(skills)


def extract_projects(text):
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    projects = []
    in_projects = False
    current = None

    stop_headers = {
        "EDUCATION", "EXPERIENCE", "CERTIFICATIONS",
        "ACHIEVEMENTS", "EXTRA CURRICULAR ACTIVITIES"
    }

    for line in lines:
        if line.upper() == "PROJECTS":
            in_projects = True
            continue

        if in_projects and line.upper() in stop_headers:
            break

        if not in_projects:
            continue

        if line.startswith("•"):
            if current:
                current["description"] += " " + line.lstrip("•").strip()
        else:
            if current:
                projects.append(current)
            current = {"title": line, "description": ""}

    if current:
        projects.append(current)

    return projects


def parse_resume(text):
    email = re.search(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", text)
    phone = re.search(r"\b\d{10}\b", text)

    lines = [l.strip() for l in text.split("\n") if l.strip()]

    return {
        "name": lines[0] if lines else "Candidate",
        "email": email.group(0) if email else "",
        "phone": phone.group(0) if phone else "",
        "skills": extract_skills(text),
        "projects": extract_projects(text)
    }