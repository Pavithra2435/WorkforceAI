"""
================================================================================
WorkforceAI - Enterprise Application Runner
Launches the High-Performance REST API Server and Serves the Modern HTML5/CSS/JS UI.
================================================================================
"""

import os
import sys
import uvicorn

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("🚀 Launching WorkforceAI Platform (Pure HTML5, CSS3 & JavaScript UI)")
    print("👉 Web Application: http://localhost:8000")
    print("👉 REST API Status:  http://localhost:8000/api/status")
    print("=" * 70 + "\n")
    uvicorn.run("backend.api_server:app", host="127.0.0.1", port=8000, reload=False)

