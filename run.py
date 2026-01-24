import sys
import os
from pathlib import Path

# Force project root into PYTHONPATH
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

# Import the app from main.py
from main import app

# This is needed for Render to find the app
__all__ = ["app"]