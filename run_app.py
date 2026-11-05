"""
Unified 1-Click Launcher for the Black Carbon Intelligence & Predictor Platform.
Runs the high-speed FastAPI server serving both the REST AI and the Vite React frontend.

Usage:
    python run_app.py
"""
import os
import sys
import time
import webbrowser
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parent

def check_frontend():
    dist_dir = ROOT / "frontend" / "dist"
    if not dist_dir.exists() or not (dist_dir / "index.html").exists():
        print("📦 Frontend build not found. Building Vite React app...")
        npm_cmd = "npm.cmd" if sys.platform == "win32" else "npm"
        try:
            subprocess.run([npm_cmd, "run", "build"], cwd=str(ROOT / "frontend"), check=True)
            print("✅ Frontend built successfully!")
        except Exception as e:
            print(f"⚠️ Could not automatically build frontend: {e}")
            print("Please run: cd frontend ; npm install ; npm run build")

def main():
    print("=" * 70)
    print("🌫️  BLACK CARBON INTELLIGENCE — VARANASI / INDO-GANGETIC PLAIN")
    python_sub = "AI Virtual Sensor · Forecasts · Episode Warnings · Source Split"
    print("    " + python_sub)
    python_sub_2 = "Author: Dhanav Kumar, NIT Raipur · IIT (BHU) Varanasi"
    print("    " + python_sub_2)
    print("=" * 70)
    
    check_frontend()

    import uvicorn
    
    port = int(os.environ.get("PORT", 8000))
    url = f"http://localhost:{port}"
    print(f"\n🚀 Starting server at {url}")
    print(f"📖 API Documentation: {url}/docs")
    python_msg = "Press Ctrl+C to stop the server."
    print(python_msg + "\n")

    import threading
    def open_browser():
        time.sleep(1.5)
        try:
            webbrowser.open(url)
        except Exception:
            pass

    threading.Thread(target=open_browser, daemon=True).start()

    uvicorn.run("src.api:app", host="0.0.0.0", port=port, reload=False)

if __name__ == "__main__":
    main()
