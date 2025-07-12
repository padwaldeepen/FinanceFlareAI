from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # App settings
    APP_NAME: str = "FinanceFlareAI"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost/financeflareai"
    
    # Security
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://financeflareai.vercel.app"
    ]
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # OpenAI
    OPENAI_API_KEY: str = ""
    
    # Redis (for caching and Celery)
    REDIS_URL: str = "redis://localhost:6379"
    
    # External APIs
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings() 