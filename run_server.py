"""Run the backend and print status so output is visible."""
import sys
import os

# Ensure we're in the app directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.getcwd())

print("Loading app...", flush=True)
try:
    from app.main import app
    print("App loaded. Starting Uvicorn on http://127.0.0.1:8000 ...", flush=True)
except Exception as e:
    print(f"Failed to load app: {e}", flush=True)
    sys.exit(1)

import uvicorn
uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
