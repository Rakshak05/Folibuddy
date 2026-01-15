from pathlib import Path
import html
from .utils.formatters import format_description_html


def generate_portfolio(resume):
    desktop = Path.home() / "Desktop"
    folder = desktop / "Personal Portfolio"
    folder.mkdir(exist_ok=True)

    # Safe fallbacks
    name = resume.get("name", "Candidate")
    email = resume.get("email", "")
    phone = resume.get("phone", "")
    skills = resume.get("skills", [])
    projects = resume.get("projects", [])
    links = resume.get("links", {})

    skills_html = (
        "".join(f"<li>{html.escape(skill)}</li>" for skill in skills)
        if skills else "<li>Not provided</li>"
    )

    projects_html = ""
    if projects:
        for p in projects:
            title = html.escape(p.get('title', 'Untitled'))
            
            # Convert description (list or string) to HTML
            desc = p.get('description', [])
            if isinstance(desc, list):
                description_html = format_description_html(desc)
            else:
                # Fallback for string descriptions
                description_html = f"<p>{html.escape(desc)}</p>"
            
            projects_html += f"""
            <div class="project">
                <h3>{title}</h3>
                {description_html}
            </div>
            """
    else:
        projects_html = "<p>Projects will be added soon.</p>"

    links_html = ""
    for label, url in links.items():
        if url:
            links_html += f'<li><a href="{url}" target="_blank">{label}</a></li>'

    index_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{name} | Portfolio</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>

<header>
    <h1>{name}</h1>
    <p>{email} {(" | " + phone) if phone else ""}</p>
</header>

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
    <ul>
        {links_html if links_html else "<li>No links provided</li>"}
    </ul>
</section>

</body>
</html>
"""

    style_css = """
body {
    font-family: Arial, sans-serif;
    margin: 40px;
    background: #f9f9f9;
}

header {
    border-bottom: 2px solid #333;
    margin-bottom: 20px;
}

h1 {
    margin-bottom: 5px;
}

.project {
    background: white;
    padding: 10px;
    margin-bottom: 10px;
    border-radius: 6px;
}
"""

    (folder / "index.html").write_text(index_html, encoding="utf-8")
    (folder / "style.css").write_text(style_css, encoding="utf-8")

    print(f"Portfolio generated at: {folder}")
    return str(folder)