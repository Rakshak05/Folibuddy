import sys
from pathlib import Path

# Add both root and backend to Python path
ROOT = Path(__file__).resolve().parent
BACKEND = ROOT / "backend"

sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(BACKEND))

# Import the app from backend/main.py
from main import app

# This is needed for Render to find the app
__all__ = ["app"]
