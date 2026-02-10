# Folibuddy - AI-Powered Resume to Portfolio Generator

An AI-powered web application that transforms PDF resumes into beautiful, customizable personal portfolios. Folibuddy uses Google Gemini 2.0 Flash to intelligently parse resume content, extract structured data, and generate publish-ready portfolio websites.

**🌐 Live Demo:** [https://folibuddy.onrender.com/](https://folibuddy.onrender.com/)

## 🚀 Core Features

- **PDF Resume Upload** → Extracts text and hyperlinks from PDF files
- **AI-Powered Parsing** → Uses Google Gemini 2.0 Flash to extract projects, experience, research
- **Interactive Editor** → Users can edit extracted data before generating portfolio
- **Portfolio Generation** → Creates a static HTML/CSS portfolio website ready for GitHub Pages
- **Profile Image Support** → Optional profile image upload and integration
- **AI Description Generator** → Enhance project descriptions using AI

---

## 📋 Table of Contents

1. [Tech Stack](#-tech-stack)
2. [High-Level Architecture](#-high-level-architecture)
3. [Complete Workflow](#-complete-workflow)
4. [File Structure & Responsibilities](#-file-structure--responsibilities)
5. [Detailed Pipeline Steps](#-detailed-pipeline-steps)
6. [API Endpoints](#-api-endpoints)
7. [Data Flow Diagram](#-data-flow-diagram)
8. [Installation & Setup](#-installation--setup)
9. [Troubleshooting](#-troubleshooting)
10. [Future Enhancements](#-future-enhancements)

---

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern, high-performance web framework for building APIs
- **Uvicorn** - Lightning-fast ASGI server for running FastAPI applications
- **Jinja2** - Powerful template engine for HTML rendering
- **Requests** - HTTP client library for API communication
- **Python-Multipart** - Multipart form data parsing for file uploads

### PDF Processing
- **pdfplumber** - Advanced text extraction from PDF documents
- **PyPDF2** - Hyperlink and annotation extraction from LaTeX-generated PDFs

### AI/LLM
- **Google Gemini API** - Advanced AI for intelligent resume parsing and content extraction
- **SDK Version**: `google-genai` 1.61.0+ (released January 30, 2026)
- **Model Used**: `gemini-2.0-flash` - Latest Google Gemini model for structured data extraction

### Frontend
- **HTML5** - Modern semantic markup
- **CSS3** - Advanced styling and responsive design
- **Vanilla JavaScript** - Dynamic interactivity without framework dependencies

### Data Storage
- **JSON** - Lightweight data persistence for portfolio information

---

## 🏗️ High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER UPLOADS PDF                         │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 1: PDF EXTRACTION (resume_parser.py)                      │
│  - Extract text using pdfplumber                                │
│  - Extract hyperlinks using PyPDF2                              │
│  - Combine text + hyperlinks                                    │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 2: LLM PARSING (llm_gemini_parser.py)                     │
│  - Send raw text to Google Gemini API                           │
│  - Extract: Projects, Research, Experience                      │
│  - Classify and structure data                                  │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 3: DATA STORAGE (portfolio_generator.py)                  │
│  - Save extracted data to output/portfolio.json                 │
│  - Single source of truth for all portfolio data                │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 4: EDITOR (editor.html)                                   │
│  - Display extracted data in editable form                      │
│  - Allow user to add/edit/remove content                        │
│  - Upload optional profile image                                │
│  - Generate project descriptions using AI                       │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 5: PORTFOLIO GENERATION (portfolio.py)                    │
│  - Load template.html                                           │
│  - Render with Jinja2 using user data                           │
│  - Copy CSS and assets                                          │
│  - Output to Desktop/Personal Portfolio/                        │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📝 Complete Workflow

### Stage 1: Upload & Extraction
1. User navigates to `http://127.0.0.1:8000/`
2. Lands on `frontend/upload.html` (upload page)
3. User selects PDF resume file
4. Form submits to `/upload-resume-web` endpoint
5. Backend extracts text + hyperlinks from PDF

### Stage 2: AI Parsing
1. Raw text sent to `parse_resume(text)` function
2. Regex extractors pull: name, email, phone, skills, links
3. **LLM extractor** (`extract_projects_with_llm`) sends text to Ollama
4. LLM returns structured JSON with:
   - **Projects** (title, description, repo)
   - **Research** (title, description)
   - **Experience** (company, role, dates, description, skills)

### Stage 3: Data Persistence
1. Extracted data saved to `output/portfolio.json`
2. This becomes the **single source of truth**
3. Data includes: name, email, phone, skills, projects, experience, research, links

### Stage 4: Interactive Editing
1. User sees `backend/templates/editor.html`
2. All extracted fields displayed in editable form
3. User can:
   - Edit any text field
   - Add/remove projects
   - Add custom links
   - Upload profile image
   - Generate AI descriptions for projects (via `/generate-description`)

### Stage 5: Final Generation
1. User clicks "Generate Portfolio"
2. Form data POST to `/generate` endpoint
3. Backend:
   - Parses form data
   - Updates `portfolio.json`
   - Calls `generate_portfolio(resume)`
4. Portfolio generator:
   - Loads `template.html` (Jinja2 template)
   - Renders with user data
   - Copies CSS files
   - Saves to `Desktop/Personal Portfolio/`
5. User receives success message with file path

---

## 📂 File Structure & Responsibilities

```
Folibuddy/
│
├── run.py                          # Application entry point
├── README.md                       # Project documentation (this file)
├── PIPELINE_DOCUMENTATION.md       # Detailed technical documentation
│
├── backend/                        # Core backend logic
│   ├── main.py                     # FastAPI app & routes
│   ├── resume_parser.py            # PDF text extraction
│   ├── llm_project_extractor.py    # LLM-based project extraction
│   ├── portfolio.py                # Portfolio HTML generation
│   ├── portfolio_generator.py      # Data persistence (JSON save/load)
│   ├── llm_generator.py            # AI description generator
│   ├── requirements.txt            # Python dependencies
│   ├── utils/
│   │   └── formatters.py           # Text formatting utilities
│   └── templates/
│       ├── editor.html             # Interactive editor page
│       └── template.html           # Portfolio HTML template
│
├── frontend/                       # Static frontend files
│   ├── upload.html                 # Initial upload page
│   ├── script.js                   # Frontend JavaScript
│   └── style.css                   # Basic styles
│
├── static/                         # Static assets
│   ├── template-style.css          # Portfolio CSS
│   └── uploads/                    # User-uploaded images
│
├── output/                         # Generated data
│   └── portfolio.json              # Extracted resume data
│
└── test_extraction.py              # Diagnostic test script
```

---

## 🔧 Detailed Pipeline Steps

### 1. **run.py** - Application Launcher
**Purpose**: Start the FastAPI server

```python
# Adds project root to Python path
# Starts uvicorn server on http://127.0.0.1:8000
# Enables hot reload for development
```

**Key Details**:
- Host: `127.0.0.1`
- Port: `8000`
- Reload: `True` (watches for file changes)

---

### 2. **backend/main.py** - API Routes & Orchestration
**Purpose**: Central FastAPI application with all endpoints

#### Key Endpoints:

##### `GET /` 
- Returns `frontend/upload.html`
- Entry point for users

##### `POST /upload-resume-web`
- **Input**: PDF file (multipart/form-data)
- **Process**:
  1. Extract text from PDF
  2. Parse resume with LLM
  3. Save to `output/portfolio.json`
  4. Format descriptions for editor
  5. Return editor HTML
- **Output**: Rendered `editor.html` with extracted data

##### `POST /generate`
- **Input**: Form data from editor
- **Process**:
  1. Parse all form fields (projects, experience, skills, etc.)
  2. Handle profile image upload
  3. Update `portfolio.json`
  4. Generate portfolio HTML
- **Output**: Success message + file path

##### `POST /generate-description`
- **Input**: JSON `{title, repo_url, current_description}`
- **Process**: Calls LLM to generate/enhance project description
- **Output**: JSON `{description}`

##### `GET /portfolio`
- **Input**: None
- **Process**: Loads `portfolio.json` and renders `template.html`
- **Output**: Portfolio preview (HTML)

---

### 3. **backend/resume_parser.py** - PDF Text Extraction
**Purpose**: Extract all text and hyperlinks from PDF

#### Functions:

##### `extract_text_from_pdf(file)`
- Uses **pdfplumber** to extract text
- Uses **PyPDF2** to extract hyperlinks (annotations)
- Appends hyperlinks to text for later extraction
- **Essential for**: LaTeX-generated PDFs with embedded links

##### `extract_name(text)`
- Scans first 8 lines of resume
- Looks for 2-5 word sequences (typical names)
- Excludes lines with "email", "phone", etc.

##### `extract_email(text)`
- Regex: `[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}`

##### `extract_phone(text)`
- Regex: `\b\d{10}\b` (10-digit numbers)

##### `extract_skills(text)`
- Matches against predefined skill vocabulary
- Includes: Python, C, C++, Java, TensorFlow, React, etc.

##### `extract_links(text)`
- Finds explicit URLs: `https?://...`
- Infers usernames: "GitHub: username" → `https://github.com/username`
- Returns structured dict with github, linkedin, leetcode, website, custom

##### `parse_resume(text)`
- **Main orchestrator** for resume parsing
- Calls `extract_projects_with_llm()` for complex parsing
- Returns complete structured data

---

### 4. **backend/llm_project_extractor.py** - LLM Parser
**Purpose**: Extract projects, research, and experience using AI

#### Key Functions:

##### `extract_projects_with_llm(full_text)`
- **Step 1**: Detect "PROJECTS" and "EXPERIENCE" sections
- **Step 2**: Find section end (before EDUCATION/SKILLS)
- **Step 3**: Normalize text (fix PDF wrapping issues)
- **Step 4**: Send to Ollama LLM with structured prompt
- **Step 5**: Parse JSON response
- **Step 6**: Classify items into projects, research, experience
- **Step 7**: Validate and return

**LLM Prompt Structure**:
```
Task: Clean and classify pre-extracted resume content
Rules:
- Don't remove content
- Don't merge items
- Don't split items
- Classify into: project, research, or experience

Output JSON schema:
{
  "projects": [{title, description[], repo}],
  "research": [{title, description[]}],
  "experience": [{company, role, from, to, description[], skills[]}]
}
```

##### `normalize_project_text(text)`
- Merges wrapped lines (PDF extraction artifact)
- Collapses multiple spaces
- Fixes bullet point continuation

##### `is_project_title(line)`
- Strict detection to avoid false positives
- Rejects bullets, long lines, action verbs
- Must contain 3+ letters

##### `extract_bullets(lines)`
- Merges multi-line bullets that wrap across lines

---

### 5. **backend/portfolio_generator.py** - Data Persistence
**Purpose**: Save/load portfolio data as JSON

##### `save_portfolio_data(data)`
- Creates `output/` directory if missing
- Writes `portfolio.json` with UTF-8 encoding
- Pretty-printed with 2-space indent

##### `load_portfolio_data()`
- Reads `output/portfolio.json`
- Returns None if file doesn't exist

**Data Schema**:
```json
{
  "name": "string",
  "email": "string",
  "phone": "string",
  "headline": "string",
  "about": "string",
  "skills": ["string"],
  "links": {
    "github": "url",
    "linkedin": "url",
    "custom": [{"label": "", "url": ""}]
  },
  "projects": [
    {
      "title": "string",
      "description": ["string"],
      "repo": "url"
    }
  ],
  "experience": [
    {
      "company": "string",
      "role": "string",
      "from": "date",
      "to": "date",
      "description": ["string"],
      "skills": ["string"]
    }
  ],
  "research": [
    {
      "title": "string",
      "description": ["string"]
    }
  ],
  "profile_image": "/uploads/filename.jpg"
}
```

---

### 6. **backend/portfolio.py** - HTML Generation
**Purpose**: Render final portfolio website

##### `generate_portfolio(resume)`
- **Step 1**: Load Jinja2 template (`template.html`)
- **Step 2**: Prepare portfolio data with defaults
- **Step 3**: Render HTML with template engine
- **Step 4**: Fix CSS paths for static generation
- **Step 5**: Create output folder (`Desktop/Personal Portfolio/`)
- **Step 6**: Write `index.html`
- **Step 7**: Copy `template-style.css`
- **Step 8**: Copy profile image (if exists)
- **Step 9**: Generate `README.md` with deployment instructions

**Output Structure**:
```
Desktop/Personal Portfolio/
├── index.html              # Main portfolio page
├── template-style.css      # Styles
├── uploads/
│   └── profile.jpg         # User's profile image
└── README.md               # Deployment guide
```

---

### 7. **backend/templates/editor.html** - Interactive Editor
**Purpose**: Editable form for all extracted data

**Key Features**:
- Pre-filled with extracted data
- Dynamic project/experience addition
- Profile image upload
- AI description generator button
- Custom link management
- Real-time form validation

**JavaScript Functions**:
- `addProject()` - Dynamically add project fields
- `removeProject(index)` - Remove project
- `addCustomLink()` - Add custom link field
- `generateDescription(index)` - Call AI endpoint for descriptions

---

### 8. **backend/templates/template.html** - Portfolio Template
**Purpose**: Jinja2 template for final portfolio

**Sections**:
1. Hero Section (name, headline, profile image)
2. About Section
3. Skills Grid
4. Projects Showcase (with repo links)
5. Experience Timeline
6. Research/Publications
7. Contact Links

**Template Variables**:
- `{{ name }}`
- `{{ headline }}`
- `{{ about }}`
- `{{ skills }}` (loop)
- `{{ projects }}` (loop)
- `{{ experience }}` (loop)
- `{{ research }}` (loop)
- `{{ links }}`

---

### 9. **frontend/upload.html** - Initial Upload Page
**Purpose**: Landing page with resume upload form

**Form**:
- File input (accepts PDF only)
- Submit button
- Posts to `/upload-resume-web`
- Uses `multipart/form-data` encoding

---

### 10. **backend/llm_generator.py** - AI Description Generator
**Purpose**: Enhance project descriptions using LLM

##### `enhance_project_description(title, current_desc, repo_url)`
- Sends project context to LLM
- Requests professional, concise description
- Returns formatted description text

##### `check_ollama_available()`
- Pings Ollama API
- Returns True if service is running

---

## 🌐 API Endpoints

| Method | Endpoint | Input | Output | Purpose |
|--------|----------|-------|--------|---------|
| GET | `/` | None | HTML | Serve upload page |
| POST | `/upload-resume-web` | PDF file | HTML (editor) | Parse resume & show editor |
| POST | `/generate` | Form data | JSON | Generate portfolio |
| POST | `/generate-description` | JSON | JSON | AI description generation |
| GET | `/portfolio` | None | HTML | Preview portfolio |

---

## 📊 Data Flow Diagram

```
┌─────────┐
│ PDF File│
└────┬────┘
     │
     ▼
┌──────────────────┐
│ resume_parser.py │──┐
└──────────────────┘  │
                      │ Raw Text
                      ▼
         ┌───────────────────────────┐
         │ llm_project_extractor.py  │
         │ (Ollama LLM)              │
         └────────────┬──────────────┘
                      │
                      │ Structured Data
                      ▼
         ┌────────────────────────┐
         │ portfolio_generator.py │
         │ (Save JSON)            │
         └────────────┬───────────┘
                      │
                      │ portfolio.json
                      ▼
              ┌──────────────┐
              │ editor.html  │
              │ (User Edits) │
              └──────┬───────┘
                     │
                     │ Edited Data
                     ▼
              ┌──────────────┐
              │ portfolio.py │
              │ (Jinja2)     │
              └──────┬───────┘
                     │
                     ▼
        ┌────────────────────────┐
        │ Desktop/Personal       │
        │ Portfolio/index.html   │
        └────────────────────────┘
```

---

## 💻 Installation & Setup

### Prerequisites
- Python 3.8+
- Google Gemini API key (Get one at "https://aistudio.google.com/app/apikey")
- Git (optional)

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/Rakshak05/Folibuddy.git
   cd Folibuddy
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   
   **Note**: If upgrading from an older version, ensure you have `google-genai>=1.61.0`:
   ```bash
   pip install --upgrade google-genai
   ```

3. **Set up Gemini API key**
   ```bash
   # Option 1: Export as environment variable
   export GEMINI_API_KEY="your-api-key-here"
   
   # Option 2: Create a .env file in project root
   echo "GEMINI_API_KEY=your-api-key-here" > .env
   ```

4. **Run the application**
   ```bash
   python run.py
   ```

5. **Access the application**
   - Open your browser and navigate to `http://127.0.0.1:8000/`

---

## 🐛 Troubleshooting

### Issue: "Error reading PDF" or "Resume parsing failed" (After Jan 30, 2026)
**Cause**: Breaking changes in `google-genai` library version 1.61.0 released on January 30, 2026.

**Solution**:
1. **Update the library**:
   ```bash
   pip install --upgrade google-genai>=1.61.0
   ```
2. **Verify installation**:
   ```bash
   pip show google-genai
   # Should show version 1.61.0 or higher
   ```
3. If your code is from before Feb 2026, pull the latest updates from the repository

### Issue: "Cannot connect to Gemini API"
**Solution**:
1. Check if your API key is set: `echo $GEMINI_API_KEY`
2. Verify API key is valid at [Google AI Studio](https://aistudio.google.com/)
3. Ensure you have internet connection for API calls

### Issue: "No projects extracted"
**Causes**:
1. PDF doesn't have "PROJECTS" section
2. Section is named differently (e.g., "PERSONAL PROJECTS")
3. Gemini API failed to parse

**Solution**:
- Check `llm_project_extractor.py` line 136 regex
- Add alternative keywords
- Run `test_extraction.py` to debug

### Issue: "Profile image not showing"
**Causes**:
1. Image path incorrect in JSON
2. Image not copied to output folder
3. CSS path issue

**Solution**:
- Check `output/portfolio.json` → `profile_image` field
- Verify `Desktop/Personal Portfolio/uploads/` contains image
- Check `portfolio.py` line 58-70 (image copy logic)

### Issue: "Experience not extracted"
**Solution**:
1. Ensure "EXPERIENCE" keyword exists in resume
2. Check if LLM is classifying as "projects" instead
3. Review Gemini prompt in `llm_gemini_parser.py`

---

## 🔍 Development Tips

### Testing LLM Extraction
Run diagnostic test:
```bash
python test_extraction.py
```

### Debugging PDF Extraction
Check what's being extracted:
```python
# Add to resume_parser.py after extract_text_from_pdf
print("DEBUG: Extracted text:")
print(text[:1000])  # First 1000 chars
```

### Viewing Portfolio Data
Check the JSON:
```bash
cat output/portfolio.json
# or on Windows
type output\portfolio.json
```

### Modifying Portfolio Template
- Edit: `backend/templates/template.html`
- Edit styles: `static/template-style.css`
- Server auto-reloads on changes

---

## 🚀 Future Enhance`m`ents

1. **Multiple Templates**: Support for different portfolio styles
2. **Cover Letter Generator**: AI-generated cover letters
3. **SEO Optimization**: Meta tags and structured data
4. **Dark Mode**: Theme toggle
5. **Export to PDF**: Portfolio as PDF resume
6. **GitHub Deploy**: One-click GitHub Pages deployment
7. **Analytics**: Track portfolio views
8. **Multi-language Support**: International resume parsing
9. **Custom Themes**: User-customizable color schemes
10. **Cloud Storage Integration**: Save portfolios to cloud

---

## 📄 License

This project is under active development.

---

## 👨‍💻 Author & Credits

**Project**: Folibuddy  
**Repository**: [github.com/Rakshak05/Folibuddy](https://github.com/Rakshak05/Folibuddy)  
**Tech Stack**: FastAPI, Google Gemini API, Jinja2, pdfplumber, PyPDF2  
**LLM Model**: gemini-2.0-flash

---

**Last Updated**: February 9, 2026  
**Version**: 1.1.0 (Updated for google-genai 1.61.0+ compatibility)