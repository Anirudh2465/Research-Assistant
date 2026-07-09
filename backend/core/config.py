from pydantic_settings import BaseSettings
from pathlib import Path
from .paths import BASE_DIR


class Settings(BaseSettings):
    """
    Fix #16: Use pydantic-settings BaseSettings for type-validated, auto-loaded config.
    Values are read from environment variables or from a .env file at the project root.
    """
    # API
    API_HOST: str = "127.0.0.1"
    API_PORT: int = 8000

    # CELERY / Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BACKEND: str = "redis://localhost:6379/1"

    # NEO4J
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "password"

    # LLM
    LLM_BASE_URL: str = "http://localhost:1234/v1"
    LLM_API_KEY: str = "local-llm"
    LLM_MODEL: str = "openai-oss-20b"

    model_config = {
        "env_file": str(BASE_DIR / ".env"),
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


settings = Settings()
