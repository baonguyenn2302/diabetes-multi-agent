"""Nạp quan hệ triệu chứng từ data/knowledge/graph/triples.csv vào Neo4j.

Chạy từ thư mục backend: python scripts/load_neo4j.py
MERGE nên chạy lại nhiều lần vẫn không tạo bản sao.
Mỗi source_id phải tồn tại trong data/knowledge/text/ để tránh trích dẫn sai.
"""
import csv
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = BACKEND_DIR.parent
sys.path.insert(0, str(BACKEND_DIR))

from services.neo4j_service import Neo4jService  # noqa: E402

TRIPLES = REPO_ROOT / "data" / "knowledge" / "graph" / "triples.csv"
TEXT_DIR = REPO_ROOT / "data" / "knowledge" / "text"

MERGE_CYPHER = """
MERGE (d:Disease {name: $disease})
MERGE (s:Symptom {name: $symptom})
MERGE (d)-[r:HAS_SYMPTOM]->(s)
SET r.source_id = $source_id,
    r.source_title = $source_title,
    r.section = $section,
    r.evidence = $evidence
"""


def read_rows() -> list[dict]:
    with TRIPLES.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    missing = sorted({r["source_id"] for r in rows
                      if not (TEXT_DIR / f"{r['source_id']}.md").is_file()})
    if missing:
        raise SystemExit(f"Thiếu file nguồn trong data/knowledge/text: {missing}")
    return rows


def main() -> None:
    rows = read_rows()
    svc = Neo4jService()
    health = svc.health()
    if health["status"] != "ok":
        raise SystemExit(f"Neo4j chưa sẵn sàng: {health['detail']}")
    try:
        for row in rows:
            svc.run(MERGE_CYPHER, row)
    finally:
        svc.close()
    print(f"Đã nạp {len(rows)} quan hệ HAS_SYMPTOM")


if __name__ == "__main__":
    main()