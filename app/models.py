from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class SettingsUpdate(BaseModel):
    ai_provider: Optional[str] = None
    ollama_base_url: Optional[str] = None
    ollama_model: Optional[str] = None
    linkedin_access_token: Optional[str] = None
    linkedin_person_urn: Optional[str] = None
    user_name: Optional[str] = None
    user_headline: Optional[str] = None
    user_avatar_url: Optional[str] = None

class SettingsResponse(BaseModel):
    ai_provider: str = "ollama"
    ollama_base_url: str = "http://127.0.0.1:11434"
    ollama_model: str = "qwen2.5:14b"
    ollama_online: bool = False
    ollama_available_models: List[str] = []
    linkedin_token_masked: str = ""
    has_linkedin_token: bool = False
    linkedin_person_urn: str = ""
    user_name: str = ""
    user_headline: str = ""
    user_avatar_url: str = ""

class PostItemGenerated(BaseModel):
    hook: str
    content: str
    angle: Optional[str] = "Practical Insight"
    estimated_read_time: Optional[str] = "1 min"
    hashtags: Optional[List[str]] = Field(default_factory=list)
    image_url: Optional[str] = None

class BatchGenerateRequest(BaseModel):
    topic: str
    count: int = Field(default=3, ge=1, le=5)
    angle: str = "Practical Insight"
    custom_notes: Optional[str] = ""
    provider: Optional[str] = None

class BatchGenerateResponse(BaseModel):
    posts: List[PostItemGenerated]
    is_mock: bool = False
    message: Optional[str] = None
    provider: Optional[str] = "ollama"

class RefinePostRequest(BaseModel):
    content: str
    instruction: str
    provider: Optional[str] = None

class RefinePostResponse(BaseModel):
    success: bool
    refined: str
    provider: Optional[str] = "ollama"

class PostCreate(BaseModel):
    topic: Optional[str] = "Untitled Post"
    content: str
    status: Optional[str] = "draft"
    scheduled_at: Optional[str] = None
    image_url: Optional[str] = None

class PostUpdate(BaseModel):
    topic: Optional[str] = None
    content: Optional[str] = None
    status: Optional[str] = None
    scheduled_at: Optional[str] = None
    published_at: Optional[str] = None
    linkedin_post_urn: Optional[str] = None
    error_message: Optional[str] = None
    image_url: Optional[str] = None

class PostResponse(BaseModel):
    id: int
    topic: Optional[str] = None
    content: str
    status: str
    scheduled_at: Optional[str] = None
    published_at: Optional[str] = None
    linkedin_post_urn: Optional[str] = None
    error_message: Optional[str] = None
    image_url: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class LinkedInVerifyRequest(BaseModel):
    token: Optional[str] = None

class LinkedInVerifyResponse(BaseModel):
    valid: bool
    name: Optional[str] = None
    email: Optional[str] = None
    person_urn: Optional[str] = None
    picture: Optional[str] = None
