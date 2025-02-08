from typing import Optional, List
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Chatbot Service"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = "dev-secret-key"  # Change in production
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@db:5432/chatbot"
    
    # LLM Configuration
    OLLAMA_BASE_URL: str = "http://ollama:11434"
    LLM_MODEL: str = "llama2"  # or any other model available in Ollama
    LLM_TEMPERATURE: float = 0.7
    
    # Redis Configuration (for rate limiting and caching)
    REDIS_URL: Optional[str] = "redis://redis:6379"
    
    # Debug mode
    DEBUG: bool = False
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 100
    RATE_LIMIT_PER_HOUR: int = 1000
    
    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]
    
    # Logging
    LOG_LEVEL: str = "INFO"
    JSON_LOGS: bool = True
    
    # Admin Configuration
    ADMIN_TOKEN: str = "your-secret-admin-token"  # Change this in production
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings() 