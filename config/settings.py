"""Pydantic settings and configuration loader."""

from pydantic import BaseSettings
from typing import Dict, Optional
import os


class Settings(BaseSettings):
    """Application settings."""
    
    # LLM Configuration
    llm_provider: str = "anthropic"  # "anthropic" or "openai"
    llm_model: str = "claude-3-sonnet-20240229"
    anthropic_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    
    # Agent Configuration
    max_iterations: int = 10
    temperature: float = 0.7
    max_tokens: int = 1024
    
    # Tool Configuration
    tools_enabled: Dict[str, bool] = {
        "calculator": True,
        "weather": True,
        "search": True,
    }
    
    # API Configuration
    openweather_api_key: Optional[str] = None
    serpapi_key: Optional[str] = None
    
    # Logging
    verbose: bool = True
    log_level: str = "INFO"
    
    class Config:
        """Pydantic config."""
        env_file = ".env"
        case_sensitive = False
    
    @classmethod
    def from_env(cls):
        """Load settings from environment."""
        return cls(
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            openweather_api_key=os.getenv("OPENWEATHER_API_KEY"),
            serpapi_key=os.getenv("SERPAPI_KEY"),
        )


def load_settings() -> Settings:
    """Load application settings."""
    return Settings.from_env()
