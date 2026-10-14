from fastapi import APIRouter, HTTPException
from app import ai_manager
from app.models import BatchGenerateRequest, BatchGenerateResponse, RefinePostRequest, RefinePostResponse

router = APIRouter(prefix="/api/generate", tags=["AI Generation & Studio"])

@router.post("/batch", response_model=BatchGenerateResponse)
async def generate_batch(payload: BatchGenerateRequest):
    if not payload.topic or not payload.topic.strip():
        raise HTTPException(status_code=400, detail="The topic or main idea is required.")

    try:
        result = await ai_manager.generate_batch(
            topic=payload.topic.strip(),
            count=payload.count,
            angle=payload.angle,
            custom_notes=payload.custom_notes or "",
            provider=payload.provider
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/refine", response_model=RefinePostResponse)
async def refine_post(payload: RefinePostRequest):
    if not payload.content or not payload.instruction:
        raise HTTPException(status_code=400, detail="Content and instruction are required.")

    try:
        result = await ai_manager.refine_post(
            content=payload.content,
            instruction=payload.instruction,
            provider=payload.provider
        )
        return {
            "success": True,
            "refined": result["refined"],
            "provider": result.get("provider", "ollama")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
