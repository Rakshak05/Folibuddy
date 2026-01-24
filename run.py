import sys
import os
import uvicorn
from pathlib import Path

# Force project root into PYTHONPATH
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "main:app", 
        host="0.0.0.0",
        port=port,
        reload=False 
    )
