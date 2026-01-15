"""
Formatters for project descriptions and text cleaning.
Handles conversion between list, text, and HTML formats.
"""


def clean_text(text: str) -> str:
    """Clean and normalize text by collapsing whitespace."""
    return " ".join(text.split())


def format_description_html(description_list):
    """Convert list[str] → HTML bullets for portfolio"""
    if not description_list:
        return ""
    return "<ul>" + "".join(f"<li>{point}</li>" for point in description_list) + "</ul>"


def format_description_text(desc):
    """
    Accepts:
    - list[str]
    - str

    Returns:
    - formatted string
    """
    if isinstance(desc, list):
        return "\n".join(f"• {d.strip()}" for d in desc if d.strip())
    return desc.strip()


def parse_description_from_text(text):
    """Convert edited bullet text → list[str]"""
    if not text:
        return []
    return [
        line.lstrip("-• ").strip()
        for line in text.split("\n")
        if line.strip()
    ]
