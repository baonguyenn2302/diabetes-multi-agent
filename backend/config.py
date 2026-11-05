"""Environment-based configuration for the Step 5 Flask + SQLite MVP."""
from __future__ import annotations
import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

class Config:
    JSON_AS_ASCII = False
    MAX_CONTENT_LENGTH = 64 * 1024
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
    OLLAMA_TIMEOUT = float(os.getenv("OLLAMA_TIMEOUT", "90"))
    CHROMA_PATH = os.getenv("CHROMA_PATH", str(REPO_ROOT / "chroma_db"))
    NEO4J_URI = os.getenv("NEO4J_URI", "")
    NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
    # Read the password only from the environment, never from committed config.
    NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "")
    SQLITE_PATH = os.getenv("SQLITE_PATH", str(REPO_ROOT / "data" / "chat_history.sqlite3"))
    FRONTEND_ORIGINS = [s.strip() for s in os.getenv("FRONTEND_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",") if s.strip()]
