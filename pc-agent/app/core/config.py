"""Configuration management for PC build recommendation system."""
import os
from typing import Optional, List
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings."""

    
    APP_NAME: str = "PC Build Recommendation System - Algeria"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"

    
    API_V1_PREFIX: str = "/api/v1"
    ALLOWED_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/pc_builds_dz"

    
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CACHE_TTL: int = 3600  

    
    LLM_PROVIDER: str = "gemini"  
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    TOGETHER_API_KEY: Optional[str] = None
    TOGETHER_MODEL: str = "mistralai/Mixtral-8x22B-Instruct-v0.1"
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-1.5-flash"  # or gemini-1.5-pro
    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_TOKENS: int = 2000

    
    OUEDKNISS_BASE_URL: str = "https://www.ouedkniss.com"
    SCRAPER_USER_AGENT: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    SCRAPER_DELAY_SECONDS: float = 2.0
    SCRAPER_MAX_RETRIES: int = 3

    
    DEFAULT_CURRENCY: str = "DZD"
    USD_TO_DZD_RATE: float = 135.0  
    EUR_TO_DZD_RATE: float = 145.0

    
    DEFAULT_LOCALE: str = "fr"
    SUPPORTED_LOCALES: List[str] = ["ar", "fr", "en"]

   
    WORKER_COUNT: int = 4
    MAX_CONNECTIONS: int = 100

    
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

   
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()



settings = get_settings()


GEMINI_API_KEY = settings.GEMINI_API_KEY
