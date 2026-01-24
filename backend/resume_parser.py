import pdfplumber
import re
import os


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
    # Replace weird PDF garbage
    text = re.sub(r"\(cid:\d+\)", " ", text)

    # Normalize spaces but KEEP newlines
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{2,}", "\n", text)

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
        "Python", "C", "C++", "Java", "Kotlin", "JavaScript", "HTML", "CSS", "MongoDB", 
        "SQL", "TensorFlow", "PyTorch", "Scikit-Learn", "Pandas", "NumPy", "Matplotlib", 
        "React", "Nest.js", "FastAPI", "Firebase", "Git", "Docker", "Machine Learning", 
        "Deep Learning", "LLM", "NLP"
    ]

    found = set()
    text_lower = text.lower()

    for skill in KNOWN_SKILLS:
        if skill.lower() in text_lower:
            found.add(skill)

    return sorted(found)


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
    """Parse resume text and extract structured data using Gemini API.
    
    Returns:
        dict: Dictionary containing name, email, phone, skills, projects, and links
    """
    
    try:
        from backend.llm_gemini_parser import parse_resume_gemini
        
        print("🔵 Using Gemini API for resume parsing...")
        result = parse_resume_gemini(text)
        
        # Gemini returns everything, we're done!
        print(f"✅ Gemini parsed: {result.get('name', 'Unknown')}")
        return result
        
    except Exception as e:
        print(f"❌ Gemini API failed: {e}")
        raise Exception(
            f"Resume parsing failed. Please ensure GEMINI_API_KEY is set in your .env file. Error: {str(e)}"
        )
