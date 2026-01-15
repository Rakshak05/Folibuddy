from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from typing import List

from backend.resume_parser import extract_text_from_pdf, parse_resume
from backend.utils.formatters import clean_text
from backend.portfolio import generate_portfolio
from backend.llm_generator import check_ollama_available, enhance_project_description

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
async def upload_resume_web(file: UploadFile = File(...)):
    """Handle web upload - parse resume and return editor."""
    try:
        # Extract text from PDF
        text = extract_text_from_pdf(file.file)
        
        # Parse resume (includes LLM project extraction)
        from .resume_parser import parse_resume
        data = parse_resume(text)
        
        print(f"DEBUG: Extracted name: {data.get('name')}")
        print(f"DEBUG: Extracted email: {data.get('email')}")
        print(f"DEBUG: Extracted {len(data.get('skills', []))} skills")
        print(f"DEBUG: Extracted {len(data.get('projects', []))} projects")
        print(f"DEBUG: Extracted links: {data.get('links')}")
        
        # Convert project descriptions to editable text format
        from .utils.formatters import format_description_text
        for project in data.get("projects", []):
            desc = project.get("description", [])
            if isinstance(desc, list):
                project["description"] = format_description_text(desc)
            # If it's already a string, leave it as is
        
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
    
    resume = {
        "name": name,
        "email": email,
        "phone": phone,
        "skills": skills_list,
        "projects": projects,
        "links": links
    }

    # Generate portfolio
    portfolio_path = generate_portfolio(resume)

    return {
        "message": "Personal portfolio generated successfully",
        "path": portfolio_path
    }


@app.post("/generate-description")
async def generate_description_endpoint(request: Request):
    """Generate project description using AI on demand."""
    try:
        data = await request.json()
        title = data.get("title", "").strip()
        repo_url = data.get("repo_url", "").strip()
        current_description = data.get("current_description", "").strip()
        
        if not title:
            return JSONResponse(
                status_code=400,
                content={"error": "Project title is required"}
            )
        
        # Check if title is too short/generic
        if len(title) < 3:
            return JSONResponse(
                status_code=400,
                content={"error": "Insufficient content - title too short for AI generation"}
            )
        
        # Check if Ollama is available
        if not check_ollama_available():
            return JSONResponse(
                status_code=503,
                content={"error": "AI service unavailable. Please ensure Ollama is running."}
            )
        
        # Generate description
        description = enhance_project_description(title, current_description, repo_url)
        
        # Check if description is meaningful
        if not description or len(description.strip()) < 10:
            return JSONResponse(
                status_code=400,
                content={"error": "Unable to generate meaningful content from provided information"}
            )
        
        return JSONResponse(content={"description": description})
    
    except Exception as e:
        print(f"Error generating description: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "An error occurred while generating the description"}
        )