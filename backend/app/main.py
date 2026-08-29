from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database.database import engine
from app.database.models import Base
from pathlib import Path

from fastapi.staticfiles import StaticFiles

from app.api.routes import router as analysis_router
Base.metadata.create_all(
    bind=engine
)

app = FastAPI(
    title="VisionGuard API",
    description="AI-Powered Image Quality & Defect Detection API",
    version="1.0.0"
)

BASE_DIR = Path(__file__).resolve().parents[1]

UPLOAD_DIR = BASE_DIR / "uploads"

UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

app.mount(
    "/uploads",
    StaticFiles(
        directory=str(UPLOAD_DIR)
    ),
    name="uploads",
)

app.include_router(analysis_router)


@app.get("/")
def root():
    return {
        "message": "VisionGuard API is running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "VisionGuard API",
        "version": "1.0.0"
    }
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)