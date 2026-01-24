import os
import uuid
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
import shutil

BASE_OUTPUT_DIR = os.getenv(
    "PORTFOLIO_OUTPUT_DIR",
    "backend/temp"
)

def generate_portfolio_files(portfolio_data: dict) -> str:
    """
    Generate portfolio HTML files in an isolated temp directory.
    
    Args:
        portfolio_data: Dictionary containing resume/portfolio data
        
    Returns:
        str: Path to the generated portfolio folder
    """
    # Create unique portfolio ID
    portfolio_id = str(uuid.uuid4())
    output_dir = os.path.join(BASE_OUTPUT_DIR, portfolio_id)
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Setup Jinja2 environment
    template_dir = Path(__file__).parent.parent / "templates"
    env = Environment(loader=FileSystemLoader(str(template_dir)))
    
    # Use modern portfolio template
    template_name = "template.html"
    template = env.get_template(template_name)
    
    # Ensure all required fields have defaults
    portfolio_context = {
        "name": portfolio_data.get("name", "Portfolio"),
        "headline": portfolio_data.get("headline", ""),
        "about": portfolio_data.get("about", ""),
        "email": portfolio_data.get("email", ""),
        "phone": portfolio_data.get("phone", ""),
        "skills": portfolio_data.get("skills", []),
        "projects": portfolio_data.get("projects", []),
        "experience": portfolio_data.get("experience", []),
        "research": portfolio_data.get("research", []),
        "links": portfolio_data.get("links", {}),
        "profile_image": portfolio_data.get("profile_image", None)
    }
    
    # Render HTML from template
    html_content = template.render(**portfolio_context)
    
    # Fix CSS paths for static file generation
    html_content = html_content.replace('href="/static/template-style.css"', 'href="template-style.css"')
    
    # Write index.html
    index_path = os.path.join(output_dir, "index.html")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    # Copy CSS file from static folder
    static_dir = Path(__file__).parent.parent.parent / "static"
    styles_source = static_dir / "template-style.css"
    styles_dest = Path(output_dir) / "template-style.css"
    
    if styles_source.exists():
        shutil.copy(styles_source, styles_dest)
    
    # Copy profile image if it exists
    if portfolio_context["profile_image"]:
        image_filename = portfolio_context["profile_image"].split("/")[-1]
        source_image = static_dir / "uploads" / image_filename
        
        if source_image.exists():
            # Create uploads folder in output
            uploads_folder = Path(output_dir) / "uploads"
            uploads_folder.mkdir(exist_ok=True)
            
            dest_image = uploads_folder / image_filename
            shutil.copy(source_image, dest_image)
    
    # Create README
    readme_content = f"""# {portfolio_context['name']} — Personal Portfolio

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
- Edit `template-style.css` to change styling
- Replace profile image in `uploads/` folder if needed
"""
    
    readme_path = os.path.join(output_dir, "README.md")
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    print(f"✅ Portfolio generated at: {output_dir}")
    
    return output_dir
