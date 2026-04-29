import os
from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache


BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class Settings(BaseSettings):
    PROJECT_NAME: str = "Memorise Digital Avatar API"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/memorise"
    
    ALIYUN_API_KEY: Optional[str] = None
    ALIYUN_BASE_URL: str = "https://dashscope.aliyuncs.com/api/v1"
    ALIYUN_WS_URL: str = "wss://dashscope.aliyuncs.com/api-ws/v1/realtime"
    ALIYUN_IMAGE_MODEL: str = "wanx-v1"
    ALIYUN_TEXT_MODEL: str = "qwen-plus"
    
    AVATAR_GENERATION_MODEL: str = "wanx-v1"
    FACE_ANALYSIS_MODEL: str = "qwen-vl-plus"
    
    VOICE_ENROLLMENT_MODEL: str = "qwen-voice-enrollment"
    VOICE_TTS_MODEL: str = "qwen3-tts-flash-realtime"
    VOICE_TTS_INSTRUCT_MODEL: str = "qwen3-tts-instruct-flash-realtime"
    VOICE_TARGET_MODEL: str = "qwen3.5-omni-plus-realtime"
    VOICE_DEFAULT_VOICE: str = "Cherry"
    
    MAX_RETRY_COUNT: int = 3
    RETRY_DELAY_SECONDS: int = 60
    
    UPLOAD_DIR: str = os.path.join(BASE_DIR, "uploads")
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024
    
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
