import os
from pathlib import Path

# Base Directory (research-os root)
# resolving logic: paths.py is in backend/core/paths.py
# so parent -> core, parent -> backend, parent -> research-os
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Storage Directories
STORAGE_DIR = BASE_DIR / "storage"
PDF_DIR = STORAGE_DIR / "pdfs"
IMAGE_DIR = STORAGE_DIR / "images"
EMBEDDING_DIR = STORAGE_DIR / "embeddings"
CACHE_DIR = STORAGE_DIR / "cache"

# Ensure directories exist
for directory in [STORAGE_DIR, PDF_DIR, IMAGE_DIR, EMBEDDING_DIR, CACHE_DIR]:
    directory.mkdir(parents=True, exist_ok=True)
