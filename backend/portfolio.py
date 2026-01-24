from pathlib import Path
from jinja2 import Environment, FileSystemLoader
import shutil
import os
import uuid

BASE_OUTPUT_DIR = os.getenv(
    "PORTFOLIO_OUTPUT_DIR",
    "backend/temp"
)

def generate_portfolio(resume):
    """
    Generate a static portfolio website using template selection.
    Uses Workfolio template if profile image exists, otherwise uses Simple template.
    """
    # Setup Jinja2 environment
    template_dir = Path(__file__).parent / "templates"
    env = Environment(loader=FileSystemLoader(str(template_dir)))
    
    # Using modern portfolio template
    template_name = "template.html"
    print(f"🎨 USING TEMPLATE: {template_name}")
    template = env.get_template(template_name)
    
    # Ensure all required fields have defaults
    portfolio_data = {
        "name": resume.get("name", "Portfolio"),
        "headline": resume.get("headline", ""),
        "about": resume.get("about", ""),
        "email": resume.get("email", ""),
        "phone": resume.get("phone", ""),
        "skills": resume.get("skills", []),
        "projects": resume.get("projects", []),
        "experience": resume.get("experience", []),  # Professional experience timeline
        "research": resume.get("research", []),
        "links": resume.get("links", {}),
        "profile_image": resume.get("profile_image", None)
    }
    
    # Render HTML from template
    html_content = template.render(**portfolio_data)
    
    # Fix CSS paths for static file generation
    html_content = html_content.replace('href="/static/template-style.css"', 'href="template-style.css"')
    
    # Create output folder using environment variable or default temp directory
    portfolio_id = str(uuid.uuid4())
    folder = Path(BASE_OUTPUT_DIR) / portfolio_id
    folder.mkdir(parents=True, exist_ok=True)
    
    # Write index.html
    (folder / "index.html").write_text(html_content, encoding="utf-8")
    
    # Copy CSS file from static folder
    static_dir = Path(__file__).parent.parent / "static"
    styles_source = static_dir / "template-style.css"
    styles_dest = folder / "template-style.css"
    
    if styles_source.exists():
        shutil.copy(styles_source, styles_dest)
    
    # Copy profile image if it exists
    if portfolio_data["profile_image"]:
        # Profile image path is like "/uploads/filename.jpg"
        # We need to copy from static/uploads/filename.jpg
        image_filename = portfolio_data["profile_image"].split("/")[-1]
        source_image = static_dir / "uploads" / image_filename
        
        if source_image.exists():
            # Create uploads folder in output
            uploads_folder = folder / "uploads"
            uploads_folder.mkdir(exist_ok=True)
            
            dest_image = uploads_folder / image_filename
            shutil.copy(source_image, dest_image)
    
    # Create README
    readme_content = f"""# {portfolio_data['name']} — Personal Portfolio

This website was generated automatically using Folibuddy.

## Template Used
{template_name.replace('_new', '').replace('.html', '').title()}

## How to View
Simply open `index.html` in your web browser.

## How to Publish
1. Create a new GitHub repository
2. Upload all files from this folder
3. Go to repository Settings → Pages
4. Select "main" branch as source
5. Your portfolio will be live at `https://yourusername.github.io/repository-name`

## Customization
- Edit `index.html` to modify content
- Edit `styles.css` to change styling
- Replace profile image in `uploads/` folder if needed
"""
    
    (folder / "README.md").write_text(readme_content, encoding="utf-8")
    
    print(f"✅ Portfolio generated at: {folder}")
    print(f"📄 Template used: {template_name}")
    
    return str(folder)
