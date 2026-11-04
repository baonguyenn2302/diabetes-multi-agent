"""Kho tri thức ChromaDB: lưu và truy vấn các đoạn tài liệu đã nạp."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

# backend/services/chroma_service.py -> parents[2] là thư mục gốc của repo
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PERSIST_DIR = REPO_ROOT / "chroma_db"
DEFAULT_COLLECTION = "diabetes_knowledge"
DEFAULT_EMBEDDING_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"


class KnowledgeUnavailableError(RuntimeError):
    """Kho tri thức chưa sẵn sàng (rỗng hoặc không mở được)."""


class KnowledgeStore:
    def __init__(
        self,
        persist_dir: str | Path = DEFAULT_PERSIST_DIR,
        collection_name: str = DEFAULT_COLLECTION,
        embedding_model: str = DEFAULT_EMBEDDING_MODEL,
    ):
        self.persist_dir = Path(persist_dir)
        self.collection_name = collection_name
        self._embedding_fn = SentenceTransformerEmbeddingFunction(model_name=embedding_model)
        self._client = chromadb.PersistentClient(path=str(self.persist_dir))

    def _get_collection(self):
        return self._client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=self._embedding_fn,
            metadata={"hnsw:space": "cosine"},
        )

    def replace_all(
        self,
        documents: list[str],
        ids: list[str],
        metadatas: list[dict[str, Any]],
    ) -> int:
        """Xóa collection cũ rồi nạp lại toàn bộ. Trả về số đoạn sau khi nạp."""
        try:
            self._client.delete_collection(self.collection_name)
        except Exception:
            pass  # collection chưa tồn tại thì không cần xóa
        collection = self._get_collection()
        collection.add(ids=ids, documents=documents, metadatas=metadatas)
        return collection.count()

    def count(self) -> int:
        return self._get_collection().count()

    def health(self) -> dict[str, str]:
        try:
            n = self.count()
        except Exception as exc:
            return {"status": "unavailable", "detail": str(exc)}
        if n == 0:
            return {"status": "empty", "detail": "Chưa nạp tài liệu. Chạy scripts/ingest_knowledge.py"}
        return {"status": "ok", "detail": f"{n} đoạn tri thức"}

    def query(self, question: str, top_k: int = 4) -> list[dict[str, Any]]:
        """Trả về các đoạn gần nhất kèm khoảng cách (càng nhỏ càng liên quan)."""
        collection = self._get_collection()
        total = collection.count()
        if total == 0:
            raise KnowledgeUnavailableError("Kho tri thức rỗng")
        res = collection.query(query_texts=[question], n_results=min(top_k, total))
        hits = []
        for doc, meta, dist in zip(res["documents"][0], res["metadatas"][0], res["distances"][0]):
            hits.append({"document": doc, "distance": float(dist), **meta})
        return hits