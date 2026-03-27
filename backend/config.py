"""Application configuration management"""
import json
from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings from environment variables"""
    
    # API
    API_TITLE: str = "VoxAI API"
    API_VERSION: str = "2.0.0"
    API_DESCRIPTION: str = "Advanced Voice AI Assistant with Real-time Features"
    DEBUG: bool = False
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/voxai"
    DATABASE_ECHO: bool = False
    
    # Redis (caching & real-time)
    REDIS_URL: str = "redis://localhost:6379"
    
    # Authentication
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_HOURS: int = 24
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # LLM & AI
    OPENAI_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None
    DEFAULT_MODEL: str = "gpt-3.5-turbo"
    
    # Voice
    ENABLE_STT: bool = True
    ENABLE_TTS: bool = True
    DEFAULT_VOICE: str = "en-US"
    
    # File Upload
    MAX_FILE_SIZE: int = 52428800  # 50MB
    ALLOWED_EXTENSIONS: str = "pdf,txt,docx,pptx"
    UPLOAD_DIR: str = "data/uploads"
    
    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://localhost:3000"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    SENTRY_DSN: Optional[str] = None
    
    # Analytics
    ENABLE_ANALYTICS: bool = True

    @staticmethod
    def _parse_csv_or_json(value: str) -> list[str]:
        """Allow list values from JSON arrays or comma-separated strings."""
        if not value:
            return []
        cleaned = value.strip()
        if not cleaned:
            return []
        if cleaned.startswith("["):
            parsed = json.loads(cleaned)
            return [str(item).strip() for item in parsed if str(item).strip()]
        return [item.strip() for item in cleaned.split(",") if item.strip()]

    @property
    def allowed_origins(self) -> list[str]:
        return self._parse_csv_or_json(self.ALLOWED_ORIGINS)

    @property
    def allowed_extensions(self) -> list[str]:
        return self._parse_csv_or_json(self.ALLOWED_EXTENSIONS)
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
