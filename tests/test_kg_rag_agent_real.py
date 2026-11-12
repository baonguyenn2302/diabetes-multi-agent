"""Test với Neo4j THẬT (Aura). Tự bỏ qua nếu chưa kết nối được hoặc chưa nạp KB."""
import pytest
from app.config import settings


def _agent_or_skip():
    try:
        from app.agents.kg_rag_agent import KGRAGAgent
        agent = KGRAGAgent.from_settings()
        agent._load()
    except Exception as e:
        pytest.skip(f"Không kết nối được Neo4j: {type(e).__name__}")
    if not agent._entities:
        agent.close()
        pytest.skip("Neo4j chưa có KB: chạy python scripts/load_kb.py")
    return agent


def test_real_neo4j_symptoms():
    agent = _agent_or_skip()
    try:
        msg = agent.run("t", "Triệu chứng của tiểu đường là gì?")
        assert msg.status == "ok"
        assert any(e["relation"] == "SYMPTOM_OF" for e in msg.evidence)
        assert all(e["source_title"] for e in msg.evidence)
    finally:
        agent.close()


def test_real_neo4j_prediabetes_thresholds():
    agent = _agent_or_skip()
    try:
        msg = agent.run("t", "HbA1c bao nhiêu thì là tiền tiểu đường")
        assert any(e["detail"].get("min_value") == 5.7 for e in msg.evidence if e["relation"] == "INDICATES")
    finally:
        agent.close()
