"""Test KG/RAG Agent bằng 'Neo4j giả' dựng từ chính dữ liệu KB (không cần kết nối mạng)."""
import pathlib, sys

from app.agents.kg_rag_agent import (KGRAGAgent, Q_ENTITIES, Q_SOURCES, Q_NEIGHBORS,
                                     format_context)

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))
import build_kb as kb

NODE = {n[0]: n for n in kb.NODES}


def fake_runner(cypher, params):
    if cypher == Q_ENTITIES:
        return [{"id": n[0], "name": n[2], "kind": n[1], "description": n[5],
                 "source_id": n[6], "terms": kb.terms_of(n)} for n in kb.NODES]
    if cypher == Q_SOURCES:
        return [{"id": s[0], "title": s[1], "url": s[3]} for s in kb.SOURCES]
    if cypher == Q_NEIGHBORS:
        eid, rows = params["id"], []
        for a, t, b, s, p in kb.RELS:
            if eid in (a, b):
                rows.append({"relation": t, "a_name": NODE[a][2], "a_kind": NODE[a][1], "a_desc": NODE[a][5],
                             "b_name": NODE[b][2], "b_kind": NODE[b][1], "props": {"source_id": s, **p}})
        return rows
    raise AssertionError("Câu truy vấn lạ")


def agent():
    return KGRAGAgent(fake_runner)


def rels(msg):
    return [e["relation"] for e in msg.evidence if e["kind"] == "relation"]


def test_every_evidence_has_source():
    for q in ["triệu chứng tiểu đường", "ai dễ bị tiểu đường type 2", "biến chứng", "xin chào"]:
        msg = agent().run("r", q)
        assert msg.status == "ok" and msg.evidence
        assert all(e["source_title"] and e["source_title"] != "Không rõ nguồn" for e in msg.evidence)
        assert all(e["source_url"] for e in msg.evidence if "project" not in e["source_title"].lower())


def test_symptom_question():
    msg = agent().run("r", "Triệu chứng của tiểu đường là gì?")
    assert msg.payload["intents"] == ["symptom"]
    assert rels(msg)[0] == "SYMPTOM_OF"
    assert any("tiểu nhiều" in e["text"] for e in msg.evidence)


def test_longest_match_prefers_prediabetes():
    a = agent()
    assert a.find_entities("tôi bị tiền tiểu đường") == ["prediabetes"]
    assert a.find_entities("tiểu đường type 2 là gì") == ["type2"]
    assert a.find_entities("tiểu đường là gì") == ["diabetes"]


def test_prediabetes_threshold_question():
    msg = agent().run("r", "Chỉ số HbA1c bao nhiêu thì bị tiền tiểu đường?")
    ev = [e for e in msg.evidence if e["relation"] == "INDICATES"]
    assert ev and any(e["detail"].get("min_value") == 5.7 and e["detail"].get("max_value") == 6.4 for e in ev)


def test_diagnosis_threshold_question():
    msg = agent().run("r", "Ngưỡng HbA1c để chẩn đoán tiểu đường")
    ev = [e for e in msg.evidence if e["relation"] == "DIAGNOSES"]
    assert any(e["detail"].get("min_value") == 6.5 for e in ev)


def test_risk_question_without_entity_defaults_to_type2():
    msg = agent().run("r", "Những ai dễ bị bệnh?")
    assert "RISK_FACTOR_FOR" in rels(msg)


def test_prevention_question_returns_advice_text():
    msg = agent().run("r", "Tôi nên ăn uống và vận động thế nào để phòng bệnh?")
    texts = " ".join(e["text"] for e in msg.evidence)
    assert "150 phút" in texts and "lành mạnh" in texts


def test_complication_question():
    msg = agent().run("r", "Biến chứng của tiểu đường nguy hiểm không?")
    assert "MAY_LEAD_TO" in rels(msg)


def test_hints_force_entity():
    msg = agent().run("r", "cho tôi lời khuyên", hints=["prediabetes"])
    assert "prediabetes" in msg.payload["entity_ids"]


def test_top_k_limits_relations():
    msg = agent().run("r", "tiểu đường", top_k=3)
    assert len([e for e in msg.evidence if e["kind"] == "relation"]) <= 3


def test_runner_failure_returns_error_not_exception():
    def broken(c, p): raise ConnectionError("mất kết nối")
    msg = KGRAGAgent(broken).run("r", "tiểu đường")
    assert msg.status == "error" and "mất kết nối" in msg.error


def test_format_context_numbers_sources():
    ctx = format_context(agent().run("r", "triệu chứng tiểu đường", top_k=2).evidence)
    assert ctx.startswith("[1]") and "Nguồn:" in ctx


def test_no_duplicate_evidence_text():
    for q in ["Tôi nên ăn uống và vận động thế nào để phòng bệnh?", "ai dễ bị tiểu đường type 2", "tiền tiểu đường"]:
        texts = [e["text"] for e in agent().run("r", q, top_k=8).evidence]
        assert len(texts) == len(set(texts)), q
