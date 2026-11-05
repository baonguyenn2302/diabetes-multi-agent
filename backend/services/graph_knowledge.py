"""Tra cứu quan hệ triệu chứng trong Neo4j."""
from __future__ import annotations

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


def lookup_symptoms(graph: Neo4jService, question: str,
                    disease: str = DEFAULT_DISEASE) -> list[dict[str, Any]]:
    """Trả về quan hệ triệu chứng phù hợp với câu hỏi.

    Câu hỏi chung ("triệu chứng", "dấu hiệu") trả về tất cả triệu chứng.
    Câu hỏi nêu tên triệu chứng cụ thể chỉ trả về triệu chứng đó.
    Ném Neo4jUnavailableError nếu không truy vấn được.
    """
    rows = graph.run(LOOKUP_CYPHER, {"disease": disease})
    q = question.casefold()
    if any(term in q for term in GENERAL_TERMS):
        return rows
    return [r for r in rows if r["name"].casefold() in q]