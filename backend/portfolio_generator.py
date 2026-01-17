import json
import os

OUTPUT_DIR = "output"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "portfolio.json")

def save_portfolio_data(data: dict):
    """Save portfolio data to JSON file."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print("✅ Portfolio data saved to output/portfolio.json")


def load_portfolio_data():
    """Load portfolio data from JSON file."""
    if not os.path.exists(OUTPUT_FILE):
        return None

    with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
        return json.load(f)