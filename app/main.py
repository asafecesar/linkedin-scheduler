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
from app.routers import posts, generation, settings as settings_router
from app.config import settings as config

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    scheduler_service.start_scheduler(interval_seconds=config.scheduler_interval_seconds)
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
app.include_router(settings_router.router)

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

# Mount static uploads
app.mount("/static/uploads", StaticFiles(directory=str(config.uploads_dir)), name="static_uploads")

# Mount Vue static assets if dist exists
dist_dir = config.frontend_dist_dir
if dist_dir.exists() and (dist_dir / "assets").exists():
    app.mount("/assets", StaticFiles(directory=str(dist_dir / "assets")), name="assets")

@app.get("/{full_path:path}", include_in_schema=False)
async def serve_spa(full_path: str):
    if dist_dir.exists():
        file_path = dist_dir / full_path
        if full_path and file_path.is_file():
            return FileResponse(file_path)
        index_file = dist_dir / "index.html"
        if index_file.is_file():
            return FileResponse(index_file)

    return {"message": "LinkedIn AI Scheduler API is running. Check /docs for interactive Swagger API documentation."}
