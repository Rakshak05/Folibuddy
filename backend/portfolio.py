from pathlib import Path

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

    skills_html = "\n".join(
        f"<li>{skill}</li>" for skill in resume["skills"]
    )

    projects_html = ""
    for project in resume["projects"]:
        projects_html += f"""
        <div class="project">
            <h3>{project['title']}</h3>
            <p>{project['description']}</p>
        </div>
        """

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
    <p>This portfolio was automatically generated from my resume.</p>
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
