"""
Test script for portfolio generation and ZIP functionality
"""
import os
import shutil
from services.portfolio_generator import generate_portfolio_files
from services.zip_service import zip_portfolio

def test_portfolio_generation():
    """Test that portfolio files are generated correctly"""
    
    # Sample resume data
    sample_data = {
        "name": "John Doe",
        "headline": "Full Stack Developer",
        "about": "Passionate developer with 5 years of experience",
        "email": "john.doe@example.com",
        "phone": "+1234567890",
        "skills": ["Python", "JavaScript", "React", "FastAPI"],
        "projects": [
            {
                "title": "Portfolio Generator",
                "description": ["Built an automated portfolio generator", "Used FastAPI and Jinja2"],
                "repo": "https://github.com/user/portfolio-gen"
            }
        ],
        "experience": [
            {
                "company": "Tech Corp",
                "role": "Senior Developer",
                "from": "2020",
                "to": "Present",
                "description": ["Led development team", "Improved code quality"],
                "skills": ["Python", "FastAPI"]
            }
        ],
        "research": [],
        "links": {
            "github": "https://github.com/johndoe",
            "linkedin": "https://linkedin.com/in/johndoe"
        },
        "profile_image": None
    }
    
    print("🧪 Testing portfolio generation...")
    
    # Generate portfolio
    folder_path = generate_portfolio_files(sample_data)
    
    # Check that folder exists
    assert os.path.exists(folder_path), f"Folder not created: {folder_path}"
    print(f"✅ Portfolio folder created: {folder_path}")
    
    # Check that index.html exists
    index_path = os.path.join(folder_path, "index.html")
    assert os.path.exists(index_path), "index.html not created"
    print("✅ index.html created")
    
    # Check that README exists
    readme_path = os.path.join(folder_path, "README.md")
    assert os.path.exists(readme_path), "README.md not created"
    print("✅ README.md created")
    
    # Test ZIP creation
    print("\n🧪 Testing ZIP creation...")
    zip_path = zip_portfolio(folder_path)
    
    # Check that ZIP exists
    assert os.path.exists(zip_path), f"ZIP not created: {zip_path}"
    print(f"✅ ZIP created: {zip_path}")
    
    # Cleanup
    print("\n🧹 Cleaning up test files...")
    shutil.rmtree(folder_path, ignore_errors=True)
    if os.path.exists(zip_path):
        os.remove(zip_path)
    print("✅ Cleanup complete")
    
    print("\n✨ All tests passed!")

if __name__ == "__main__":
    test_portfolio_generation()
