import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Justitia Lens API"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    
    # Database
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "admin"
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: str = "5432"
    POSTGRES_DB: str = "justitia_lens"
    
    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    
    # AI
    GEMINI_API_KEY: str = "placeholder_key"
    AI_PROVIDER: str = "ollama" # Options: "gemini", "ollama", "cloudqwen"
    OLLAMA_BASE_URL: str = "http://localhost:11434/api"
    OLLAMA_MODEL: str = "llama3.1:8b"
    OLLAMA_VISION_MODEL: str = "llava"
    OLLAMA_API_KEY: str = ""  # Optional, for Ollama cloud
    
    # CloudQwen
    CLOUDQWEN_API_KEY: str = "placeholder_key"
    CLOUDQWEN_BASE_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    CLOUDQWEN_MODEL: str = "qwen-plus"
    CLOUDQWEN_VISION_MODEL: str = "qwen-vl-plus"
    
    # Storage
    STORAGE_DIR: str = os.path.join(os.getcwd(), "data")

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

settings = Settings()
