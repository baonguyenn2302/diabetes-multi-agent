"""Tra cứu quan hệ triệu chứng trong Neo4j."""
from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from services.neo4j_service import Neo4jService

DEFAULT_DISEASE = "đái tháo đường típ 2"
GENERAL_TERMS = ("triệu chứng", "dấu hiệu", "symptom")

LOOKUP_CYPHER = """
MATCH (d:Disease {name: $disease})-[r:HAS_SYMPTOM]->(s:Symptom)
RETURN s.name AS name, r.source_id AS source_id, r.source_title AS source_title,
       r.section AS section, r.evidence AS evidence
ORDER BY name
"""
TRIPLES_CSV = Path(__file__).resolve().parents[2] / "data" / "knowledge" / "graph" / "triples.csv"


def _matching_symptoms(rows: list[dict[str, Any]], question: str) -> list[dict[str, Any]]:
    q = question.casefold()
    if any(term in q for term in GENERAL_TERMS):
        return rows
    return [row for row in rows if row["name"].casefold() in q]


def lookup_symptoms(graph: Neo4jService, question: str,
                    disease: str = DEFAULT_DISEASE) -> list[dict[str, Any]]:
    """Trả về quan hệ triệu chứng phù hợp với câu hỏi.

    Câu hỏi chung ("triệu chứng", "dấu hiệu") trả về tất cả triệu chứng.
    Câu hỏi nêu tên triệu chứng cụ thể chỉ trả về triệu chứng đó.
    Ném Neo4jUnavailableError nếu không truy vấn được.
    """
    rows = graph.run(LOOKUP_CYPHER, {"disease": disease})
    return _matching_symptoms(rows, question)


def lookup_local_symptoms(
    question: str,
    disease: str = DEFAULT_DISEASE,
    path: str | Path = TRIPLES_CSV,
) -> list[dict[str, Any]]:
    """Use the checked-in graph triples when the optional Neo4j service is unavailable."""
    with Path(path).open(encoding="utf-8", newline="") as stream:
        rows = [
            {
                "name": row["symptom"],
                "source_id": row["source_id"],
                "source_title": row["source_title"],
                "section": row["section"],
                "evidence": row["evidence"],
            }
            for row in csv.DictReader(stream)
            if row["disease"] == disease
        ]
    return _matching_symptoms(rows, question)