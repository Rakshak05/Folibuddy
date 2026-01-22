import json
from backend.llm_project_extractor import extract_projects_with_llm

# A fake resume to test if the LLM is actually working
SAMPLE_RESUME = """
RAKSHAK KUMAR
Software Engineer

EXPERIENCE
Software Intern | Google | June 2024 - Present
• Built a full-stack dashboard using React and TypeScript.
• Optimized database queries, reducing latency by 40%.

Machine Learning Engineer | Startup XYZ | Jan 2023 - May 2024
• Developed NLP models for sentiment analysis.
• Deployed models to production serving 10K+ users.

PROJECTS
Folibuddy | AI Portfolio Assistant
• Developed an AI app using Gemini API to analyze resumes.
• Built frontend with Next.js and backend with Python.

E-Commerce Platform | Full Stack Web App
• Created a full-stack shopping platform with React and Node.js.
• Integrated Stripe payments and user authentication.

RESEARCH
Neonatal Sepsis Detection | Research Project
• Created a machine learning model to detect sepsis in infants.
• Published results in a university journal.

SKILLS
Python, JavaScript, React, Node.js, Machine Learning, TensorFlow
"""

print("=" * 60)
print("DIAGNOSTIC TEST - LLM Extraction")
print("=" * 60)
print(f"\nTesting with {len(SAMPLE_RESUME)} characters of sample text.")
print("\nSample resume includes:")
print("  - 2 work experiences")
print("  - 2 projects")
print("  - 1 research paper")
print("\n" + "=" * 60)

# Call your function directly
result = extract_projects_with_llm(SAMPLE_RESUME)

print("\n" + "=" * 60)
print("FINAL RESULT")
print("=" * 60)
print(json.dumps(result, indent=2))

print("\n" + "=" * 60)
print("COUNTS:")
print(f"  Projects extracted: {len(result.get('projects', []))}")
print(f"  Experiences extracted: {len(result.get('experience', []))}")
print(f"  Research extracted: {len(result.get('research', []))}")
print("=" * 60)

if len(result.get('experience', [])) > 0:
    print("\n✅ SUCCESS! Experience extraction is working!")
    print("   The problem is likely in your PDF reading code.")
else:
    print("\n❌ FAILED! LLM is not extracting experience.")
    print("   Check if Ollama is running: ollama serve")
    print("   Make sure llama3 is installed: ollama pull llama3")
