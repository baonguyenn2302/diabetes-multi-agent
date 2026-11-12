"""Đọc ngưỡng từ Neo4j Aura THẬT. Tự bỏ qua nếu chưa kết nối được hoặc chưa nạp KB."""
import pytest
from app.config import settings


def _agent_or_skip():
    try:
        from app.agents.kg_rag_agent import KGRAGAgent
        kg = KGRAGAgent.from_settings()
    except Exception as e:
        pytest.skip(f"Không kết nối được Neo4j: {type(e).__name__}")
    return kg


def test_real_kg_thresholds_are_usable():
    from app.agents.rule_agent import RuleBasedAgent
    kg = _agent_or_skip()
    try:
        agent = RuleBasedAgent.from_runner(kg.query)
        m = agent.run("t", {"HbA1c_level": 6.8, "blood_glucose_level": 90.0, "age": 30, "bmi": 22.0,
                            "hypertension": 0, "heart_disease": 0, "smoking_history": "never"},
                      {"prediction": 0})
        if m.status != "ok" and "Thiếu ngưỡng" in (m.error or ""):
            pytest.skip("Neo4j chưa có KB: chạy python scripts/load_kb.py")
        assert m.status == "ok"
        assert any(f["id"] == "R01" for f in m.payload["flags"])
        assert m.payload["needs_human_review"] is True
    finally:
        kg.close()
