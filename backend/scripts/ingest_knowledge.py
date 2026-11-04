"""Nạp tài liệu trong data/knowledge/text vào ChromaDB.

Chạy từ thư mục backend:  python scripts/ingest_knowledge.py
Mỗi lần chạy nạp lại toàn bộ collection.
"""
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from services.chroma_service import REPO_ROOT, KnowledgeStore  # noqa: E402
from services.knowledge_chunker import (  # noqa: E402
    chunk_markdown,
    parse_frontmatter,
    part_number,
)

TEXT_DIR = REPO_ROOT / "data" / "knowledge" / "text"


def keep_5481(section: str, subsection: str) -> bool:
    """Chỉ giữ chẩn đoán, đánh giá và tư vấn lối sống.

    Loại bỏ phần điều trị thuốc, liều insulin và bệnh đồng mắc.
    """
    n = part_number(section)
    if n in (1, 2, 3):
        return True
    if n == 4:
        return subsection.startswith("5.")  # 5. Tư vấn lối sống, vận động, dinh dưỡng
    return False  # PHẦN 5, 6 và các mục khác chưa được duyệt


# Mỗi tài liệu: hàm lọc, hoặc None để nạp toàn bộ.
INGEST_PLAN = {
    "who_diabetes_fact_sheet_2024-11-14": None,
    "bo_y_te_qd_5481_2020_huong_dan_dtd_tip2": keep_5481,
}
# Không nạp:
#   who_wha74-4_2021_diabetes: nghị quyết chính sách, không phải tài liệu lâm sàng.
#   bo_y_te_sua_doi_bo_sung_dtd_tip2_2021: chỉ sửa PHẦN 5 (điều trị nội trú).


def main() -> None:
    documents: list[str] = []
    ids: list[str] = []
    metadatas: list[dict] = []

    for path in sorted(TEXT_DIR.glob("*.md")):
        source_id = path.stem
        if source_id not in INGEST_PLAN:
            print(f"Bỏ qua: {path.name}")
            continue

        meta, body = parse_frontmatter(path.read_text(encoding="utf-8"))
        chunks = chunk_markdown(body, INGEST_PLAN[source_id])
        for i, chunk in enumerate(chunks):
            ids.append(f"{source_id}-{i:04d}")
            documents.append(chunk.document)
            metadatas.append({
                "source_id": source_id,
                "source_title": meta.get("source_title", ""),
                "publisher": meta.get("publisher", ""),
                "date": meta.get("issued") or meta.get("published_or_updated", ""),
                "url": meta.get("original_url", ""),
                "section": chunk.section,
                "subsection": chunk.subsection,
            })
        print(f"{source_id}: {len(chunks)} đoạn")

    if not documents:
        raise SystemExit("Không có đoạn nào để nạp. Kiểm tra data/knowledge/text.")

    store = KnowledgeStore()
    total = store.replace_all(documents, ids, metadatas)
    print(f"Tổng: {total} đoạn trong collection '{store.collection_name}'")


if __name__ == "__main__":
    main()