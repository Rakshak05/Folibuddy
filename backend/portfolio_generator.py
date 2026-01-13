from pathlib import Path

def generate_portfolio_files(data, output_dir: Path):
    output_dir.mkdir(exist_ok=True)

    skills_html = "".join(f"<li>{s}</li>" for s in data["skills"])
    projects_html = "".join(
        f"<div><h3>{p['title']}</h3><p>{p['description']}</p></div>"
        for p in data["projects"]
    )

    index_html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>{data['name']} | Portfolio</title>
</head>
<body>

<h1>{data['name']}</h1>

<h2>Skills</h2>
<ul>{skills_html}</ul>

<h2>Projects</h2>
{projects_html}

</body>
</html>
"""

    (output_dir / "index.html").write_text(index_html, encoding="utf-8")