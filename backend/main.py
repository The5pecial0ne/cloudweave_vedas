# backend/main.py

import sys
from pathlib import Path
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

# 1) ensure Python can see your RIFE-Cloudweave folder
REPO_ROOT = Path(__file__).parent.parent
RIFE_API  = REPO_ROOT / "Cloudweave Runner" / "RIFE-Cloudweave-main"
sys.path.append(str(RIFE_API))

# 2) import the FastAPI app you defined
from get_wms_img_updated import app

# 3) mount the videos directory first (so /videos is matched before /)
VIDEOS_DIR = Path(__file__).parent / "videos"
VIDEOS_DIR.mkdir(exist_ok=True)
app.mount(
    "/videos",
    StaticFiles(directory=str(VIDEOS_DIR)),
    name="videos"
)

# 4) mount your HTML/CSS/JS frontend at the root
FRONTEND_DIR = REPO_ROOT / "frontend"
app.mount(
    "/",
    StaticFiles(directory=str(FRONTEND_DIR), html=True),
    name="static"
)

if __name__ == "__main__":
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
