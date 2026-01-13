from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from typing import List

from .resume_parser import extract_text_from_pdf, parse_resume
from .utils import clean_text
from .portfolio import generate_portfolio

app = FastAPI(title="Resume to Portfolio API")

# Setup Jinja2 templates
templates = Jinja2Templates(directory="backend/templates")

# Mount static files to serve frontend
app.mount("/static", StaticFiles(directory="frontend"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*", "null"],  # Allow file:// origin
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the upload page"""
    with open("frontend/upload.html", "r", encoding="utf-8") as f:
        return f.read()

@app.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    """API endpoint that returns JSON (for frontend/script.js)"""
    if not file.filename.endswith(".pdf"):
        return {"error": "Only PDF files are supported"}

    raw_text = extract_text_from_pdf(file.file)
    cleaned_text = clean_text(raw_text)
    resume_data = parse_resume(cleaned_text)

    return resume_data


@app.post("/upload-resume-web", response_class=HTMLResponse)
async def upload_resume_web(request: Request, file: UploadFile = File(...)):
    """Web endpoint that returns HTML editor page"""
    if not file.filename.endswith(".pdf"):
        return "<h1>Error: Only PDF files are supported</h1>"

    raw_text = extract_text_from_pdf(file.file)
    cleaned_text = clean_text(raw_text)
    resume_data = parse_resume(cleaned_text)

    return templates.TemplateResponse(
        "editor.html",
        {"request": request, "data": resume_data}
    )


@app.post("/generate")
async def generate(request: Request):
    """Receive edited resume data from the form"""
    
    # Get form data
    form_data = await request.form()
    
    # Extract basic info
    name = form_data.get("name", "")
    email = form_data.get("email", "")
    phone = form_data.get("phone", "")
    
    # Parse skills from comma-separated string
    skills_str = form_data.get("skills", "")
    skills_list = [s.strip() for s in skills_str.split(",") if s.strip()]
    
    # Parse projects from form data
    projects = []
    project_index = 1
    while True:
        title_key = f"project_title_{project_index}"
        desc_key = f"project_desc_{project_index}"
        
        if title_key in form_data:
            projects.append({
                "title": form_data[title_key],
                "description": form_data[desc_key]
            })
            project_index += 1
        else:
            break
    
    resume = {
        "name": name,
        "email": email,
        "phone": phone,
        "skills": skills_list,
        "projects": projects
    }

    # Generate portfolio
    portfolio_path = generate_portfolio(resume)

    return {
        "message": "Personal portfolio generated successfully",
        "path": portfolio_path
    }