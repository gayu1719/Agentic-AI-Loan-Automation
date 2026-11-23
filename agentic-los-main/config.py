"""Configuration settings for the Agentic LOS system."""
import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # API Keys
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    langfuse_public_key: str = os.getenv("LANGFUSE_PUBLIC_KEY", "")
    langfuse_secret_key: str = os.getenv("LANGFUSE_SECRET_KEY", "")
    langfuse_host: str = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
    
    # Application
    app_name: str = "Agentic LOS"
    app_version: str = "1.0.0"
    debug: bool = os.getenv("DEBUG", "True").lower() == "true"
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Database
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./agentic_los.db")
    
    # Vector Store
    vector_store_path: str = os.getenv("VECTOR_STORE_PATH", "./vector_store")
    embeddings_model: str = os.getenv("EMBEDDINGS_MODEL", "text-embedding-ada-002")
    
    # Document Processing
    ocr_language: str = os.getenv("OCR_LANGUAGE", "eng")
    max_file_size_mb: int = int(os.getenv("MAX_FILE_SIZE_MB", "50"))
    
    # Rules and Guidelines
    rules_path: str = "./rules"
    
    # Enhanced Features Configuration
    enable_advanced_modeling: bool = os.getenv("ENABLE_ADVANCED_MODELING", "false").lower() == "true"
    enable_real_time_data: bool = os.getenv("ENABLE_REAL_TIME_DATA", "false").lower() == "true"
    enable_document_ai: bool = os.getenv("ENABLE_DOCUMENT_AI", "false").lower() == "true"
    enable_risk_monitoring: bool = os.getenv("ENABLE_RISK_MONITORING", "false").lower() == "true"
    monte_carlo_simulations: bool = os.getenv("MONTE_CARLO_SIMULATIONS", "false").lower() == "true"
    
    # External API Keys for Enhanced Features
    market_data_api_key: str = os.getenv("MARKET_DATA_API_KEY", "")
    economic_data_api_key: str = os.getenv("ECONOMIC_DATA_API_KEY", "")
    credit_bureau_api_key: str = os.getenv("CREDIT_BUREAU_API_KEY", "")
    
    # Infrastructure
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    class Config:
        env_file = ".env"


settings = Settings() 