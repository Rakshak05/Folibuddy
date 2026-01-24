import pdfplumber
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import json
import re
import os


# ---------- Step 1: Extract text from PDF ----------
def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.strip()


# ---------- Step 2: Build the LLaMA prompt ----------
def build_prompt(resume_text):
    return f"""
You are a resume parser. Extract the following information and return only valid JSON — no explanations.

{{
    "Name": "",
    "Email": "",
    "Phone": "",
    "LinkedIn": "",
    "GitHub": "",
    "Education": [
        {{"Degree": "", "Institution": "", "Year": ""}}
    ],
    "Experience": [
        {{"Company": "", "Role": "", "Years": "", "Role Summary": ""}}
    ],
    "Projects": [
        {{"Title": "", "Description": "", "Technologies": []}}
    ],
    "Skills": [],
    "Extracurriculars": []
}}

Resume Text:
{resume_text}
"""


# ---------- Step 3: Initialize model ----------
def load_llama(model_id="meta-llama/Meta-Llama-3-8B-Instruct"):
    print(f"🔹 Loading model: {model_id}")
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype=torch.float16,
        device_map="auto"
    )
    return tokenizer, model


# ---------- Step 4: Run inference ----------
def run_llama(prompt, tokenizer, model, max_new_tokens=1024):
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    outputs = model.generate(
        **inputs,
        max_new_tokens=max_new_tokens,
        temperature=0.0,
        do_sample=False
    )
    raw_output = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return raw_output


# ---------- Step 5: Extract JSON safely ----------
def extract_json(text):
    # Find JSON between first and last braces
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1:
        json_text = text[start:end + 1]
        # Remove any invalid characters
        json_text = re.sub(r"[\x00-\x1f\x7f-\x9f]", "", json_text)
        try:
            return json.loads(json_text)
        except json.JSONDecodeError:
            print("⚠️ Could not decode JSON. Raw model output:\n", text)
            return None
    else:
        print("⚠️ No JSON found in model output.")
        return None


# ---------- Step 6: Main parser ----------
def parse_resume(pdf_path, model_id="meta-llama/Meta-Llama-3-8B-Instruct"):
    resume_text = extract_text_from_pdf(pdf_path)
    prompt = build_prompt(resume_text)

    tokenizer, model = load_llama(model_id)
    output = run_llama(prompt, tokenizer, model)
    parsed = extract_json(output)
    return parsed


# ---------- Step 7: Main entry ----------
if __name__ == "__main__":
    pdf_path = "C:\\Users\\RAKSHAK\\OneDrive\\Desktop\\RB_Resume.pdf"
    if not os.path.exists(pdf_path):
        print(f"❌ File not found: {pdf_path}")
        exit()

    result = parse_resume(pdf_path)
    if result:
        print("\n✅ Parsed Resume Data:\n")
        print(json.dumps(result, indent=4))
    else:
        print("❌ Parsing failed.")