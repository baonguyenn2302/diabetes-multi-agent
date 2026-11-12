"""Cấu hình tập trung. Đọc từ biến môi trường / file .env."""
import os
from dataclasses import dataclass
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def resolve_path(p: str) -> Path:
    """Đường dẫn tương đối được hiểu là tính từ thư mục gốc project."""
    path = Path(p)
    return path if path.is_absolute() else PROJECT_ROOT / path


@dataclass(frozen=True)
class Settings:
    neo4j_uri: str = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    # Neo4j Aura dùng NEO4J_USERNAME; chấp nhận cả NEO4J_USER
    neo4j_user: str = os.getenv("NEO4J_USERNAME") or os.getenv("NEO4J_USER", "neo4j")
    neo4j_password: str = os.getenv("NEO4J_PASSWORD", "password")
    neo4j_database: str = os.getenv("NEO4J_DATABASE", "neo4j")
    model_path: str = os.getenv("MODEL_PATH", "models/model.keras")
    preprocessor_path: str = os.getenv("PREPROCESSOR_PATH", "models/preprocessor.joblib")
    meta_path: str = os.getenv("MODEL_META_PATH", "models/model_meta.json")
    audit_log_path: str = os.getenv("AUDIT_LOG_PATH", "logs/audit.jsonl")
    kb_file: str = os.getenv("KB_FILE", "kb/DB_diabet.cypher")


settings = Settings()
