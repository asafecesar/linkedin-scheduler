import uuid
from pathlib import Path
from fastapi import APIRouter, HTTPException, status, UploadFile, File
from typing import List
from datetime import datetime
from app import database as db
from app import linkedin_service
from app.models import PostCreate, PostUpdate, PostResponse

from app.config import settings

router = APIRouter(prefix="/api/posts", tags=["Posts & Scheduling"])

ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".gif"}
MAX_FILE_SIZE = 15 * 1024 * 1024  # 15MB

@router.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    ext = Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format. Supported formats: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        )

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="The file exceeds the 15MB limit.")

    filename = f"{uuid.uuid4().hex}{ext}"
    dest_path = settings.uploads_dir / filename
    with open(dest_path, "wb") as f:
        f.write(content)

    return {
        "success": True,
        "url": f"/static/uploads/{filename}",
        "filename": filename,
        "size": len(content)
    }

@router.get("", response_model=List[PostResponse])
async def list_posts():
    return db.get_all_posts()

@router.post("", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(payload: PostCreate):
    if not payload.content or not payload.content.strip():
        raise HTTPException(status_code=400, detail="Post content cannot be empty.")
    post = db.create_post(
        topic=payload.topic or "Untitled Post",
        content=payload.content.strip(),
        status=payload.status or "draft",
        scheduled_at=payload.scheduled_at,
        image_url=payload.image_url
    )
    return post

@router.get("/{post_id}", response_model=PostResponse)
async def get_post(post_id: int):
    post = db.get_post_by_id(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found.")
    return post

@router.put("/{post_id}", response_model=PostResponse)
async def update_post(post_id: int, payload: PostUpdate):
    updates = payload.model_dump(exclude_unset=True)
    updated = db.update_post(post_id, updates)
    if not updated:
        raise HTTPException(status_code=404, detail="Post not found.")
    return updated

@router.delete("/{post_id}")
async def delete_post(post_id: int):
    post = db.get_post_by_id(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found.")
    db.delete_post(post_id)
    return {"success": True, "message": "Post deleted successfully."}

@router.post("/{post_id}/publish-now")
async def publish_now(post_id: int):
    post = db.get_post_by_id(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found.")

    try:
        result = await linkedin_service.publish_to_linkedin(
            content=post["content"],
            image_url=post.get("image_url")
        )
        updated = db.update_post(post_id, {
            "status": "published",
            "published_at": datetime.utcnow().isoformat() + "Z",
            "linkedin_post_urn": result.get("post_urn"),
            "error_message": None
        })
        return {"success": True, "post": updated, "result": result}
    except Exception as e:
        db.update_post(post_id, {
            "status": "failed",
            "error_message": str(e)
        })
        raise HTTPException(status_code=500, detail=f"Error publishing to LinkedIn: {str(e)}")
