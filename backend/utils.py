import re

def clean_text(text: str) -> str:
    """
    Cleans text extracted from PDFs by fixing spacing and line breaks.
    """
    text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)
    text = re.sub(r"\n(?=[a-z])", " ", text)
    text = re.sub(r"(?<=[a-z])\n", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()