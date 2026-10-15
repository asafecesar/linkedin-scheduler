from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    # Server network config
    host: str = "127.0.0.1"
    port: int = 8000
    reload: bool = False

    # Application paths
    base_dir: Path = BASE_DIR
    data_dir: Path = BASE_DIR / "data"

    # Ollama defaults
    ollama_base_url: str = "http://127.0.0.1:11434"
    ollama_model: str = "qwen2.5:14b"

    # LinkedIn optional overrides via environment variables
    linkedin_access_token: Optional[str] = None
    linkedin_person_urn: Optional[str] = None

    # Scheduler worker
    scheduler_interval_seconds: int = 30

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def uploads_dir(self) -> Path:
        p = self.data_dir / "uploads"
        p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def db_path(self) -> Path:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        return self.data_dir / "linkedin_scheduler.db"

    @property
    def frontend_dist_dir(self) -> Path:
        return self.base_dir / "frontend" / "dist"

settings = Settings()
