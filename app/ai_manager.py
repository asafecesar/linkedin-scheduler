from typing import Dict, Any, List, Optional
from app import database as db
from app import ollama_service

async def get_active_provider(requested_provider: Optional[str] = None) -> str:
    return "ollama"

async def generate_batch(
    topic: str,
    count: int = 3,
    angle: str = "Practical Insight",
    custom_notes: str = "",
    provider: Optional[str] = None
) -> Dict[str, Any]:
    res = await ollama_service.generate_batch_posts_ollama(
        topic=topic,
        count=count,
        angle=angle,
        custom_notes=custom_notes
    )
    res["provider"] = "ollama"
    return res

async def refine_post(content: str, instruction: str, provider: Optional[str] = None) -> Dict[str, Any]:
    refined = await ollama_service.refine_post_ollama(content, instruction)
    return {"refined": refined, "provider": "ollama"}
