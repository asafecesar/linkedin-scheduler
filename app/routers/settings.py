from fastapi import APIRouter, HTTPException
from app import database as db
from app import linkedin_service
from app import scheduler_service
from app import ollama_service
from app.models import SettingsUpdate, SettingsResponse, LinkedInVerifyRequest, LinkedInVerifyResponse

router = APIRouter(prefix="/api", tags=["Settings & Integrations"])

@router.get("/settings", response_model=SettingsResponse)
async def get_settings():
    settings = db.get_all_settings()
    linkedin_token = settings.get("linkedin_access_token", "")

    ollama_status = await ollama_service.check_ollama_status()

    return {
        "ai_provider": "ollama",
        "ollama_base_url": settings.get("ollama_base_url", ollama_service.DEFAULT_OLLAMA_URL),
        "ollama_model": settings.get("ollama_model", ollama_service.DEFAULT_OLLAMA_MODEL),
        "ollama_online": ollama_status.get("online", False),
        "ollama_available_models": ollama_status.get("available_models", []),
        "linkedin_token_masked": f"••••••••{linkedin_token[-4:]}" if len(linkedin_token) >= 4 else "",
        "has_linkedin_token": bool(linkedin_token),
        "linkedin_person_urn": settings.get("linkedin_person_urn", ""),
        "user_name": settings.get("user_name", ""),
        "user_headline": settings.get("user_headline", ""),
        "user_avatar_url": settings.get("user_avatar_url", "")
    }

@router.post("/settings")
async def update_settings(payload: SettingsUpdate):
    if payload.ai_provider is not None:
        db.set_setting("ai_provider", payload.ai_provider.strip())
    if payload.ollama_base_url is not None:
        db.set_setting("ollama_base_url", payload.ollama_base_url.strip())
    if payload.ollama_model is not None:
        db.set_setting("ollama_model", payload.ollama_model.strip())
    if payload.linkedin_access_token is not None:
        db.set_setting("linkedin_access_token", payload.linkedin_access_token.strip())
    if payload.linkedin_person_urn is not None:
        db.set_setting("linkedin_person_urn", payload.linkedin_person_urn.strip())
    if payload.user_name is not None:
        db.set_setting("user_name", payload.user_name.strip())
    if payload.user_headline is not None:
        db.set_setting("user_headline", payload.user_headline.strip())
    if payload.user_avatar_url is not None:
        db.set_setting("user_avatar_url", payload.user_avatar_url.strip())

    return {"success": True, "message": "Settings saved successfully!"}

@router.get("/ollama/status")
async def get_ollama_status():
    status = await ollama_service.check_ollama_status()
    return status

@router.post("/linkedin/verify", response_model=LinkedInVerifyResponse)
async def verify_linkedin(payload: LinkedInVerifyRequest):
    try:
        profile = await linkedin_service.verify_linkedin_token(payload.token)
        return profile
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/scheduler/check")
async def manual_scheduler_check():
    await scheduler_service.process_due_posts()
    return {"success": True, "message": "Scheduler check executed successfully."}
