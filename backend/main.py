from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from typing import List
import os
import shutil
import uuid

from backend.resume_parser import extract_text_from_pdf, parse_resume
from backend.utils.formatters import clean_text
from backend.portfolio import generate_portfolio
from backend.portfolio_generator import save_portfolio_data, load_portfolio_data

app = FastAPI(title="Resume to Portfolio API")

# Setup Jinja2 templates
templates = Jinja2Templates(directory="backend/templates")

# Mount static files to serve frontend and styles
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploads", StaticFiles(directory="static/uploads"), name="uploads")

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
async def upload_resume_web(file: UploadFile = File(...)):
    """Handle web upload - parse resume and return editor."""
    try:
        # Extract text from PDF
        text = extract_text_from_pdf(file.file)
        
        # Parse resume (includes LLM project extraction)
        data = parse_resume(text)
         
        
        # STEP 1: Save portfolio data (single source of truth)
        portfolio_data = {
            "name": data.get("name", ""),
            "email": data.get("email", ""),
            "phone": data.get("phone", ""),
            "links": data.get("links", {}),
            "skills": data.get("skills", []),
            "projects": data.get("projects", []),
            "experience": data.get("experience", []),  # Save experience from parsing
            "research": data.get("research", []),
            "profile_image": None  # Will be set when user uploads in editor
        }
        
        save_portfolio_data(portfolio_data)

        # Convert project descriptions to editable text format for editor
        from backend.utils.formatters import format_description_text
        for project in data.get("projects", []):
            desc = project.get("description", [])
            if isinstance(desc, list):
                project["description"] = format_description_text(desc)
        
        for research in data.get("research", []):
            desc = research.get("description", [])
            if isinstance(desc, list):
                research["description"] = format_description_text(desc)
        
        for experience in data.get("experience", []):
            desc = experience.get("description", [])
            if isinstance(desc, list):
                experience["description"] = format_description_text(desc)

        # Render editor
        from fastapi.requests import Request
        request = Request(scope={"type": "http"})
        
        return templates.TemplateResponse(
            "editor.html",
            {"request": request, "data": data}
        )
    
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return HTMLResponse(content=f"<h1>Error processing resume</h1><p>{str(e)}</p>", status_code=500)


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
    
    # Parse structured links from form data
    custom_links = []
    
    # Extract ALL custom links (dynamically added via JavaScript)
    for key in form_data.keys():
        if key.startswith("custom_label_"):
            index = key.replace("custom_label_", "")
            url_key = f"custom_url_{index}"
            
            label = form_data.get(key, "").strip()
            url = form_data.get(url_key, "").strip()
            
            # Only add if both label and URL are provided
            if label and url:
                custom_links.append({
                    "label": label,
                    "url": url
                })
    
    links = {
        "github": form_data.get("github", ""),
        "linkedin": form_data.get("linkedin", ""),
        "leetcode": form_data.get("leetcode", ""),
        "website": form_data.get("website", ""),
        "custom": custom_links
    }
    
    # Parse projects from form data with repo URLs
    projects = []
    project_index = 1
    
    from .utils.formatters import parse_description_from_text
    
    while True:
        title_key = f"project_title_{project_index}"
        desc_key = f"project_desc_{project_index}"
        repo_key = f"project_repo_{project_index}"
        
        if title_key in form_data:
            # Parse description text back to list
            desc_text = form_data.get(desc_key, "")
            desc_list = parse_description_from_text(desc_text)
            
            projects.append({
                "title": form_data[title_key],
                "description": desc_list,  # Now a list!
                "repo": form_data.get(repo_key, "")
            })
            project_index += 1
        else:
            break
    
    # Handle profile image upload
    profile_image_path = None
    if "profile_image" in form_data:
        profile_image = form_data["profile_image"]
        if hasattr(profile_image, 'filename') and profile_image.filename:
            # Ensure uploads directory exists
            os.makedirs("static/uploads", exist_ok=True)
            
            # Generate unique filename
            file_extension = os.path.splitext(profile_image.filename)[1]
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            file_path = os.path.join("static/uploads", unique_filename)
            
            # Save the file
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(profile_image.file, buffer)
            
            # Store the path relative to static
            profile_image_path = f"/uploads/{unique_filename}"
    
    # Parse experience from form data
    experience = []
    experience_index = 1
    
    while True:
        company_key = f"exp_company_{experience_index}"
        role_key = f"exp_role_{experience_index}"
        from_key = f"exp_from_{experience_index}"
        to_key = f"exp_to_{experience_index}"
        desc_key = f"exp_desc_{experience_index}"
        skills_key = f"exp_skills_{experience_index}"
        
        if company_key in form_data:
            # Parse description text to list
            desc_text = form_data.get(desc_key, "")
            desc_list = parse_description_from_text(desc_text)
            
            # Parse skills to list
            skills_text = form_data.get(skills_key, "")
            skills_list_exp = [s.strip() for s in skills_text.split(",") if s.strip()]
            
            experience.append({
                "company": form_data[company_key],
                "role": form_data[role_key],
                "from": form_data.get(from_key, ""),
                "to": form_data.get(to_key, ""),
                "description": desc_list,
                "skills": skills_list_exp
            })
            experience_index += 1
        else:
            break
    
    resume = {
        "name": name,
        "headline": form_data.get("headline", ""),
        "about": form_data.get("about", ""),
        "email": email,
        "phone": phone,
        "skills": skills_list,
        "projects": projects,
        "experience": experience,  # Add experience data
        "research": load_portfolio_data().get("research", []),  # Preserve research from parsing
        "links": links,
        "profile_image": profile_image_path
    }

    # Save updated portfolio data (including profile image)
    save_portfolio_data(resume)

    # Generate portfolio
    portfolio_path = generate_portfolio(resume)

    return {
        "message": "Personal portfolio generated successfully",
        "path": portfolio_path
    }


# STEP 4: Portfolio render endpoint
def select_template(profile_image, data):
    """
    Select portfolio template - using modern template design.
    """
    return "template.html"


@app.get("/portfolio", response_class=HTMLResponse)
async def view_portfolio(request: Request):
    """Render portfolio HTML from saved JSON data."""
    data = load_portfolio_data()

    if not data:
        return HTMLResponse("<h2>No portfolio generated yet. Please upload a resume first.</h2>")

    # Select template based on profile image presence
    template_name = select_template(data.get("profile_image"), data)

    return templates.TemplateResponse(
        template_name,
        {
            "request": request,
            **data
        }
    )

