from pathlib import Path
from .llm_generator import generate_about_me, enhance_project_description, check_ollama_available

def format_paragraphs(text):
    return "\n".join(
        f"<p>{line.strip()}</p>"
        for line in text.split("\n")
        if line.strip()
    )


def generate_portfolio(resume):
    desktop = Path.home() / "Desktop"
    folder = desktop / "Personal Portfolio"
    folder.mkdir(exist_ok=True)

    # Check if Ollama is available
    ollama_available = check_ollama_available()
    
    # Generate About Me using LLM
    about_me_text = "This portfolio was automatically generated from my resume."
    if ollama_available:
        try:
            about_me_text = generate_about_me(resume)
        except Exception as e:
            print(f"Failed to generate About Me: {e}")
    
    skills_html = "\n".join(
        f"<li>{skill}</li>" for skill in resume["skills"]
    )

    # Generate projects HTML with proper array-based descriptions
    projects_html = ""
    for project in resume["projects"]:
        title = project.get("title", "")
        repo_url = project.get("repo", "").strip()
        description = project.get("description", [])
        
        # Ensure description is always a list
        if isinstance(description, str):
            description = [description]
        
        # ONLY use LLM if description is missing and Ollama is available
        if not description and ollama_available:
            try:
                llm_desc = enhance_project_description(
                    title, 
                    "",  # Empty description
                    repo_url  # Pass repo URL for GitHub analysis
                )
                # LLM returns a string, convert to list
                if llm_desc:
                    description = [llm_desc]
            except Exception as e:
                print(f"Failed to generate project description: {e}")
        
        # Generate HTML bullets from description array
        if description:
            description_html = "<ul>"
            for point in description:
                description_html += f"<li>{point}</li>"
            description_html += "</ul>"
        else:
            description_html = ""
        
        # Add repo link if available
        repo_html = ""
        if repo_url:
            repo_html = f"<p><a href='{repo_url}' target='_blank'>Project Repository</a></p>"
        
        projects_html += f"""
        <div class="project">
            <h3>{title}</h3>
            {description_html}
            {repo_html}
        </div>
        """

    # Generate structured profile links HTML
    links_html = "<ul>\n"
    icon_map = {
        "github": "GitHub",
        "linkedin": "LinkedIn",
        "leetcode": "LeetCode",
        "website": "Website"
    }
    
    if resume.get("links"):
        # Render standard platform links
        for key in ["github", "linkedin", "leetcode", "website"]:
            url = resume["links"].get(key, "")
            if url:
                label = icon_map.get(key, key.capitalize())
                links_html += f"        <li><a href='{url}' target='_blank'>{label}</a></li>\n"
        
        # Render custom links with user-defined labels
        for custom_link in resume["links"].get("custom", []):
            if custom_link.get("url"):
                label = custom_link.get("label", "Link")
                url = custom_link["url"]
                links_html += f"        <li><a href='{url}' target='_blank'>{label}</a></li>\n"
    
    links_html += "    </ul>"

    index_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{resume['name']} | Portfolio</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>

<header>
    <h1>{resume['name']}</h1>
    <p>Personal Portfolio</p>
</header>

<section>
    <h2>About Me</h2>
    <p>{about_me_text}</p>
</section>

<section>
    <h2>Skills</h2>
    <ul>
        {skills_html}
    </ul>
</section>

<section>
    <h2>Projects</h2>
    {projects_html}
</section>

<section>
    <h2>Links</h2>
    {links_html if links_html else "<p>No links provided</p>"}
</section>

<section>
    <h2>Contact</h2>
    <p>Email: {resume['email']}</p>
    <p>Phone: {resume['phone']}</p>
</section>

<script src="script.js"></script>
</body>
</html>
"""

    style_css = """
body {
    font-family: system-ui, Arial, sans-serif;
    max-width: 1100px;
    margin: auto;
    padding: 24px;
    background-color: #f5f6f8;
}

header {
    text-align: center;
    margin-bottom: 50px;
}

section {
    background: white;
    padding: 24px;
    margin-bottom: 32px;
    border-radius: 10px;
}

h1 {
    font-size: 2.6rem;
}

h2 {
    border-bottom: 2px solid #ddd;
    padding-bottom: 6px;
}

.project {
    margin-top: 16px;
}

a {
    color: #007bff;
    text-decoration: none;
}

a:hover {
    text-decoration: underline;
}

ul {
    line-height: 1.8;
}
"""

    script_js = """
console.log("Personal portfolio loaded");
"""

    readme_md = f"""
# {resume['name']} — Personal Portfolio

This website was generated automatically from your resume.

## How to run
Open `index.html` directly or serve using:

```
python -m http.server
```

## Publishing
Push this folder to GitHub and enable GitHub Pages.
"""

    (folder / "index.html").write_text(index_html, encoding="utf-8")
    (folder / "style.css").write_text(style_css, encoding="utf-8")
    (folder / "script.js").write_text(script_js, encoding="utf-8")
    (folder / "README.md").write_text(readme_md, encoding="utf-8")

    return str(folder)
