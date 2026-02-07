import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Justitia Lens API"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    
    # Database - can use DATABASE_URL directly for production
    DATABASE_URL: str = ""  # Full connection string (optional, takes priority)
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
    STORAGE_BACKEND: str = "local"  # "local" or "supabase"
    
    # Supabase (for Storage and optionally DB)
    SUPABASE_URL: str = ""  # e.g., https://xxxxx.supabase.co
    SUPABASE_KEY: str = ""  # Service role key
    SUPABASE_BUCKET: str = "evidence"  # Storage bucket name
    
    def get_database_url(self) -> str:
        """Get the database URL, preferring DATABASE_URL if set."""
        if self.DATABASE_URL:
            # Convert postgres:// to postgresql+asyncpg:// if needed
            url = self.DATABASE_URL
            if url.startswith("postgres://"):
                url = url.replace("postgres://", "postgresql+asyncpg://", 1)
            elif url.startswith("postgresql://") and "+asyncpg" not in url:
                url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
            return url
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
            f"{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

settings = Settings()
