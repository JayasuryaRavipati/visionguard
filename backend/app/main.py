from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database.database import engine
from app.database.models import Base

from app.api.routes import router as analysis_router
Base.metadata.create_all(
    bind=engine
)

app = FastAPI(
    title="VisionGuard API",
    description="AI-Powered Image Quality & Defect Detection API",
    version="1.0.0"
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