import os
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app import database as db
from app import ollama_service
from app import linkedin_service
from app import scheduler_service
from app.routers import posts, generation, settings

BASE_DIR = Path(__file__).resolve().parent.parent

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    scheduler_service.start_scheduler(interval_seconds=30)
    yield
    # Shutdown
    scheduler_service.stop_scheduler()

app = FastAPI(
    title="LinkedIn AI Post Generator & Scheduler",
    description="Backend API inteligente para geração de posts e agendamento automático no LinkedIn com IA local.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(posts.router)
app.include_router(generation.router)
app.include_router(settings.router)

# Health Check
@app.get("/api/health", tags=["System"])
async def health_check():
    ollama_status = await ollama_service.check_ollama_status()
    token, urn = linkedin_service.get_credentials()
    return {
        "status": "ok",
        "ai_provider": "ollama",
        "ollama_online": ollama_status.get("online", False),
        "ollama_model": ollama_status.get("current_model", ""),
        "linkedin_configured": bool(token),
        "user_urn": urn or None
    }

UPLOADS_DIR = BASE_DIR / "data" / "uploads"
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
FRONTEND_DIST = BASE_DIR / "frontend" / "dist"

# Mount static uploads
app.mount("/static/uploads", StaticFiles(directory=str(UPLOADS_DIR)), name="static_uploads")

# Mount Vue static assets if dist exists
if FRONTEND_DIST.exists() and (FRONTEND_DIST / "assets").exists():
    app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIST / "assets")), name="assets")

@app.get("/{full_path:path}", include_in_schema=False)
async def serve_spa(full_path: str):
    if FRONTEND_DIST.exists():
        file_path = FRONTEND_DIST / full_path
        if full_path and file_path.is_file():
            return FileResponse(file_path)
        index_file = FRONTEND_DIST / "index.html"
        if index_file.is_file():
            return FileResponse(index_file)

    return {"message": "LinkedIn AI Scheduler API is running. Check /docs for interactive Swagger API documentation."}
