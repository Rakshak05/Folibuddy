from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from .resume_parser import extract_text_from_pdf, parse_resume
from .utils import clean_text

app = FastAPI(title="Resume to Portfolio API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def health_check():
    return {"status": "Backend is running"}

@app.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        return {"error": "Only PDF files are supported"}

    raw_text = extract_text_from_pdf(file.file)
    cleaned_text = clean_text(raw_text)
    resume_data = parse_resume(cleaned_text)

    return resume_data