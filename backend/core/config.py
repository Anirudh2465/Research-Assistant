import os
from dotenv import load_dotenv
from pathlib import Path
from .paths import BASE_DIR

# Load .env from root
load_dotenv(BASE_DIR / ".env")

class Settings:
    # API
    API_HOST = os.getenv("API_HOST", "127.0.0.1")
    API_PORT = int(os.getenv("API_PORT", 8000))

    # CELERY
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    CELERY_BACKEND = os.getenv("CELERY_BACKEND", "redis://localhost:6379/1")

    # NEO4J
    NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
    NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

    # LLM
    LLM_BASE_URL = os.getenv("LLM_BASE_URL", "http://localhost:1234/v1")
    LLM_API_KEY = os.getenv("LLM_API_KEY", "local-llm")
    LLM_MODEL = os.getenv("LLM_MODEL", "openai-oss-20b")

settings = Settings()
