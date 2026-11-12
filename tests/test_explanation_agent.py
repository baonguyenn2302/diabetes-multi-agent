"""Test Explanation Agent (template) với đầu vào dựng sẵn. Không cần Neo4j, TensorFlow."""
import pathlib, sys
from app.agents.explanation_agent import ExplanationAgent
from app.schemas import AgentMessage
from app.sources import SOURCE_TITLES

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))
import build_kb as kb

RID = "req_t"
EX = ExplanationAgent()


def pred(score=0.95, label="nguy cơ cao", p=1):
    return AgentMessage.ok(RID, "DL", {"prediction": p, "label": label, "score": score, "threshold": 0.85})


def rules(flags, review=False):
    return AgentMessage.ok(RID, "Rule", {"flags": flags, "needs_human_review": review,
                                         "conflicts": [], "n_flags": len(flags)})


def flag(fid, level, text="nội dung cờ", src="src_ada2026", cat="lab"):
    return {"id": fid, "level": level, "category": cat, "text": text, "source_id": src}


def kg(evs):
    return AgentMessage.ok(RID, "KG", {}, evidence=evs)


def ev(text, rel="SYMPTOM_OF", title="WHO – Diabetes (fact sheet)", url="https://who.int"):
    return {"kind": "relation", "relation": rel, "text": text, "source_title": title, "source_url": url}


def report(outputs):
    m = EX.run(RID, outputs)
    assert m.status == "ok"
    return m.payload["report"]


def full(**over):
    o = dict(prediction=pred(), rules=rules([flag("R01", "high", "HbA1c 8.2% ≥ 6.5%")]), knowledge=kg([ev("Khát nước là triệu chứng.")]))
    o.update(over)
    return o


def test_report_has_all_sections():
    r = report(full())
    for title in ("### 1.", "### 2.", "### 3.", "### 4.", "### 5.", "### 6."):
        assert title in r, title


def test_prediction_is_described_as_not_diagnosis():
    r = report(full())
    assert "không phải chẩn đoán xác định" in r
    assert "nguy cơ cao" in r and "0.95" in r


def test_flags_show_source_title_from_kb():
    r = report(full())
    assert SOURCE_TITLES["src_ada2026"][0] in r


def test_flags_sorted_by_level_high_first():
    r = report(full(rules=rules([flag("R03", "medium"), flag("R01", "high")])))
    assert r.index("[R01]") < r.index("[R03]")


def test_evidence_numbered_with_source():
    r = report(full())
    assert "1. Khát nước là triệu chứng." in r
    assert "Nguồn: WHO – Diabetes (fact sheet)" in r


def test_review_section_when_conflict():
    conflict = flag("C01", "review", "Model nói nguy cơ thấp nhưng HbA1c cao", cat="conflict")
    r = report(full(rules=rules([flag("R01", "high"), conflict], review=True)))
    assert "Cần chuyên gia y tế xem xét" in r
    assert "[C01]" in r


def test_no_review_message_when_consistent():
    r = report(full())
    assert "Không phát hiện mâu thuẫn" in r


def test_missing_prediction_reported_not_crash():
    m = EX.run(RID, full(prediction=AgentMessage.fail(RID, "DL", "model hỏng")))
    assert m.status == "ok"
    assert "model hỏng" in m.payload["report"]
    assert any("Dự đoán" in w for w in m.payload["warnings"])


def test_everything_missing_still_returns_ok_report():
    m = EX.run(RID, {})
    assert m.status == "ok"
    r = m.payload["report"]
    assert "Không có kết quả dự đoán" in r
    assert "Không tìm thấy bằng chứng" not in r and "Không truy xuất được bằng chứng" in r
    assert len(m.payload["warnings"]) == 3


def test_evidence_deduplicated_and_capped_at_10():
    evs = [ev(f"Bằng chứng số {i}") for i in range(15)] + [ev("Bằng chứng số 0")]
    r = report(full(knowledge=kg(evs)))
    ev_part = r.split("### 4.")[1].split("### 5.")[0]
    assert "10. Bằng chứng số 9" in ev_part
    assert "11. " not in ev_part
    assert ev_part.count("Bằng chứng số 0") == 1


def test_advice_includes_prevention_items_from_kg():
    evs = [ev("Ăn uống lành mạnh giúp phòng bệnh.", rel="HELPS_PREVENT")]
    r = report(full(knowledge=kg(evs)))
    advice = r.split("### 5.")[1].split("### 6.")[0]
    assert "Ăn uống lành mạnh giúp phòng bệnh." in advice
    assert "bác sĩ" in advice


def test_recheck_advice_when_high_flag():
    r = report(full())
    assert "làm lại xét nghiệm" in r


def test_no_medication_or_dose_recommendations():
    """Mục Giới hạn có câu phủ định về thuốc/liều, nên chỉ kiểm tra các mục khuyến nghị."""
    m = EX.run(RID, full(rules=rules([flag("R01", "high"), flag("R10", "low", "Có hút thuốc", cat="advice")])))
    sec = m.payload["sections"]
    text = " ".join(" ".join(sec[k]) for k in ("prediction", "flags", "review", "evidence", "advice")).lower()
    assert "liều" not in text and "kê đơn" not in text


def test_unknown_source_shows_placeholder():
    r = report(full(rules=rules([flag("R01", "high", src="src_khong_ton_tai")])))
    assert "Không rõ nguồn" in r


def test_payload_keys_and_sections():
    m = EX.run(RID, full())
    p = m.payload
    assert {"report", "sections", "warnings", "n_flags", "n_evidence"} <= set(p)
    assert set(p["sections"]) == {"prediction", "flags", "review", "evidence", "advice", "limits"}
    assert p["n_flags"] == 1 and p["n_evidence"] == 1 and p["warnings"] == []


def test_report_is_deterministic():
    assert report(full()) == report(full())


def test_sources_table_matches_kb():
    assert SOURCE_TITLES == {s[0]: (s[1], s[3]) for s in kb.SOURCES}
