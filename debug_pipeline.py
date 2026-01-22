import pdfplumber
import json
import os

# Import your extractor
try:
    from backend.llm_project_extractor import extract_projects_with_llm
except ImportError:
    # Fallback if file is in same folder
    from llm_project_extractor import extract_projects_with_llm

# --- CONFIGURATION ---
# REPLACE THIS with your actual resume filename
PDF_PATH = "Resume.pdf" 

def run_pipeline_test():
    print("="*60)
    print("FOLIBUDDY PIPELINE DIAGNOSTIC TEST")
    print("="*60)
    
    print(f"\n--- 1. CHECKING FILE: {PDF_PATH} ---")
    if not os.path.exists(PDF_PATH):
        print(f"❌ ERROR: File '{PDF_PATH}' not found!")
        print("Please edit the PDF_PATH variable in this script.")
        print(f"Current directory: {os.getcwd()}")
        print(f"Files in directory: {os.listdir('.')}")
        return

    print("✅ File found.")

    # --- STEP 2: TEST PDF READING ---
    print("\n--- 2. READING PDF TEXT ---")
    full_text = ""
    try:
        with pdfplumber.open(PDF_PATH) as pdf:
            print(f"   Total pages: {len(pdf.pages)}")
            for page in pdf.pages:
                text = page.extract_text(x_tolerance=2, y_tolerance=2, layout=True)
                if text:
                    full_text += text + "\n"
    except Exception as e:
        print(f"❌ CRITICAL ERROR reading PDF: {e}")
        return

    if not full_text or len(full_text) < 50:
        print("❌ FAILURE: PDF Text is empty or too short!")
        print("Possible causes:")
        print("  - PDF is scanned/image-based (needs OCR)")
        print("  - PDF is encrypted")
        print("  - PDF is corrupted")
        return
    else:
        print(f"✅ Success! Read {len(full_text)} characters.")
        print(f"\nFirst 200 characters:")
        print("-"*60)
        print(full_text[:200])
        print("-"*60)
        
        # Check for key sections
        print(f"\nSection Detection:")
        print(f"  Contains 'EXPERIENCE': {'EXPERIENCE' in full_text.upper()}")
        print(f"  Contains 'PROJECTS': {'PROJECTS' in full_text.upper()}")
        print(f"  Contains 'EDUCATION': {'EDUCATION' in full_text.upper()}")

    # --- STEP 3: TEST AI EXTRACTION ---
    print("\n--- 3. SENDING TO LLM (This may take 10-30 seconds) ---")
    try:
        data = extract_projects_with_llm(full_text)
    except ConnectionError as e:
        print(f"❌ CONNECTION ERROR: {e}")
        print("Is Ollama running? Try: ollama serve")
        return
    except Exception as e:
        print(f"❌ ERROR calling LLM: {e}")
        print("Possible causes:")
        print("  - Ollama not running (run: ollama serve)")
        print("  - llama3 not installed (run: ollama pull llama3)")
        return

    # --- STEP 4: INSPECT RESULTS ---
    print("\n--- 4. FINAL OUTPUT ---")
    
    projects = data.get("projects", [])
    experience = data.get("experience", [])
    research = data.get("research", [])
    
    print(f"\n📊 EXTRACTION RESULTS:")
    print(f"  Projects Found: {len(projects)}")
    print(f"  Experience Found: {len(experience)}")
    print(f"  Research Found: {len(research)}")
    
    if not projects and not experience and not research:
        print("\n⚠️  WARNING: LLM returned valid JSON, but all lists are empty.")
        print("\nFull LLM Response:")
        print(json.dumps(data, indent=2))
        print("\nPossible causes:")
        print("  - Resume format doesn't match expected structure")
        print("  - Sections are named differently")
        print("  - LLM prompt needs adjustment")
    else:
        print("\n✅ SUCCESS! Data Extracted:")
        print(json.dumps(data, indent=2))
        
    # --- STEP 5: RECOMMENDATIONS ---
    print("\n" + "="*60)
    print("RECOMMENDATIONS:")
    print("="*60)
    
    if len(experience) > 0:
        print("✅ Experience extraction is WORKING!")
    else:
        print("❌ Experience extraction FAILED")
        print("   Check if your resume has:")
        print("   - Clear 'EXPERIENCE' section header")
        print("   - Job entries with company names and roles")
        
    if len(projects) > 0:
        print("✅ Project extraction is WORKING!")
    else:
        print("⚠️  Project extraction returned nothing")
        print("   Check if your resume has:")
        print("   - Clear 'PROJECTS' section header")
        print("   - Project titles and descriptions")
    
    print("\n" + "="*60)
    print("NEXT STEPS:")
    print("="*60)
    if len(experience) > 0 and len(projects) > 0:
        print("✅ Everything works! Your system is ready.")
        print("   Upload resumes and they should auto-extract.")
    else:
        print("Consider using MANUAL ENTRY in the editor.")
        print("It works perfectly and gives you full control!")

if __name__ == "__main__":
    run_pipeline_test()
