from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # LLM
    anthropic_api_key: str = Field(default="", alias="ANTHROPIC_API_KEY")
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    llm_model: str = Field(default="claude-3-5-haiku-20241022", alias="LLM_MODEL")

    # Tools
    openweather_api_key: str = Field(default="", alias="OPENWEATHER_API_KEY")
    serpapi_api_key: str = Field(default="", alias="SERPAPI_API_KEY")

    # Agent behaviour
    max_iterations: int = Field(default=10, alias="MAX_ITERATIONS")
    verbose: bool = Field(default=False, alias="VERBOSE")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")


settings = Settings()