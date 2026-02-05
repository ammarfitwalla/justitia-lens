from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.config import settings
import os

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "*" # Permissive for Hackathon/Local
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for simplicity in local dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.api import upload, analyze

app.include_router(upload.router, prefix=settings.API_V1_STR, tags=["upload"])
app.include_router(analyze.router, prefix=settings.API_V1_STR, tags=["analyze"])

# Mount static files to serve evidence/report images
# This allows frontend to access files via /static/cases/{case_id}/evidence/{filename}
if os.path.exists(settings.STORAGE_DIR):
    app.mount("/static", StaticFiles(directory=settings.STORAGE_DIR), name="static")

@app.get("/")

async def root():
    return {"message": "Justitia Lens API is running"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}

