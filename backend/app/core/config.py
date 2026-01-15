from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import Optional, List, Union


class Settings(BaseSettings):
    # API
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "Procédures Maintenance Photovoltaïque"
    
    # Database
    DATABASE_URL: str = "sqlite:///./app.db"
    
    # Security
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Ollama (IA locale)
    USE_LOCAL_AI: bool = True
    OLLAMA_BASE_URL: str = "http://localhost:11434/v1"
    OLLAMA_MODEL: str = "mistral:7b-instruct-q4_K_M"
    
    # Modèles Ollama spécifiques
    OLLAMA_ENRICHMENT_MODEL: str = "mistral:7b-instruct-q4_K_M"  # Pour enrichissement IA
    OLLAMA_VISION_MODEL: str = "bakllava:7b"  # Pour analyse d'images (LLaVA)

    # Vercel / Supabase (Cloud)
    VERCEL_URL: str = "https://procedure1.vercel.app"
    VERCEL_TOKEN: Optional[str] = None
    VERCEL_PROJECT_ID: Optional[str] = None
    VERCEL_TEAM_ID: Optional[str] = None
    SUPABASE_PROJECT_ID: str = "mxxggubgvurldcneeter"
    
    # Smart Router
    ENABLE_SMART_ROUTING: bool = True
    CLASSIFICATION_TIMEOUT: float = 5.0
    
    # MCP (Model Context Protocol)
    ENABLE_MCP: bool = True
    BRAVE_API_KEY: str = "BSAV4B7OwI54Kuu9GMRO796CpPPmkC4"
    BRAVE_MCP_PORT: int = 3001
    
    # File Upload
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: set = {".jpg", ".jpeg", ".png", ".pdf", ".doc", ".docx"}
    
    # CORS
    BACKEND_CORS_ORIGINS: Union[List[str], str] = ["http://localhost:3000", "http://localhost:3001", "http://localhost:8000"]
    
    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v):
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


settings = Settings()
