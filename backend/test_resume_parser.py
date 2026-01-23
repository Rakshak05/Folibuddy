"""
Sanity check test for the new resume parser.
Run: python backend/test_resume_parser.py
"""

import sys
from pathlib import Path

# Add project root to Python path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.llm.resume_parser import parse_resume
import json

def test_resume_parser():
    """Test the resume parser with a sample PDF."""
    
    # Update this path to your actual resume PDF
    pdf_path = r"C:\Users\RAKSHAK\OneDrive\Desktop\Rakshak_Resume.pdf"
    
    try:
        print("=" * 60)
        print("🧪 Testing Resume Parser")
        print("=" * 60)
        
        result = parse_resume(pdf_path)
        
        print("\n" + "=" * 60)
        print("📋 PARSED RESULT")
        print("=" * 60)
        print(json.dumps(result, indent=2))
        
        print("\n" + "=" * 60)
        print("✅ TEST PASSED!")
        print("=" * 60)
        
    except FileNotFoundError:
        print(f"\n❌ ERROR: PDF file not found: {pdf_path}")
        print("Please update the pdf_path variable in this script.")
        sys.exit(1)
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    test_resume_parser()
