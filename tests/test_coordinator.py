"""Test Coordinator bằng agent GIẢ: kiểm tra thứ tự bước, dừng khi lỗi, và cách xử lý lỗi."""
from app.coordinator import CoordinatorAgent, DEFAULT_QUESTION
from app.schemas import AgentMessage

ORDER = []
RAW = {"gender": "Female", "age": 40}


class Stub:
    def __init__(self, name, payload=None, msg=None, exc=None, evidence=None):
        self.name, self.payload, self.msg, self.exc = name, payload or {}, msg, exc
        self.evidence = evidence or []
        self.calls = []

    def run(self, rid, *args):
        ORDER.append(self.name)
        self.calls.append((rid,) + args)
        if self.exc:
            raise self.exc
        if self.msg is not None:
            return self.msg
        return AgentMessage.ok(rid, self.name, self.payload, evidence=self.evidence)


def make(**over):
    """Tạo coordinator với 4 agent giả; `over` ghi đè từng agent hoặc explainer/monitor."""
    ORDER.clear()
    agents = dict(
        data=Stub("data", {"features": {"HbA1c_level": 5.0}}),
        dl=Stub("dl", {"prediction": 0, "label": "nguy cơ thấp", "score": 0.1}),
        rule=Stub("rule", {"flags": [], "needs_human_review": False}),
        kg=Stub("kg", evidence=[{"text": "bằng chứng", "source_title": "S", "source_url": "u"}]),
    )
    agents.update({k: v for k, v in over.items() if k in agents})
    c = CoordinatorAgent(agents["data"], agents["dl"], agents["rule"], agents["kg"],
                         explainer=over.get("explainer"), monitor=over.get("monitor"),
                         new_id=lambda: "req_fixed")
    return c, agents


def test_happy_path_runs_steps_in_order_and_status_ok():
    c, a = make()
    r = c.handle(RAW)
    assert ORDER == ["data", "dl", "rule", "kg"]
    assert r["status"] == "ok" and r["errors"] == []
    assert r["prediction"]["label"] == "nguy cơ thấp"
    assert r["rules"]["needs_human_review"] is False
    assert len(r["evidence"]) == 1


def test_validation_error_stops_before_models():
    c, a = make(data=Stub("data", msg=AgentMessage.fail("x", "data", "Thiếu feature: age")))
    r = c.handle(RAW)
    assert ORDER == ["data"]
    assert r["status"] == "validation_error"
    assert r["prediction"] is None and r["rules"] is None and r["evidence"] == []
    assert r["errors"][0]["agent"] == "data"


def test_none_input_is_validation_error():
    c, _ = make(data=Stub("data", msg=AgentMessage.fail("x", "data", "không phải dict")))
    assert c.handle(None)["status"] == "validation_error"


def test_dl_failure_continues_rule_without_prediction():
    c, a = make(dl=Stub("dl", msg=AgentMessage.fail("x", "dl", "model hỏng")))
    r = c.handle(RAW)
    assert ORDER == ["data", "dl", "rule", "kg"]
    assert a["rule"].calls[-1][2] is None            # Rule nhận prediction = None
    assert r["status"] == "partial" and r["prediction"] is None
    assert any(e["agent"] == "dl" for e in r["errors"])


def test_kg_failure_gives_partial_with_empty_evidence():
    c, _ = make(kg=Stub("kg", msg=AgentMessage.fail("x", "kg", "neo4j mất kết nối")))
    r = c.handle(RAW)
    assert r["status"] == "partial" and r["evidence"] == []
    assert r["prediction"] is not None and r["rules"] is not None


def test_rule_failure_gives_partial():
    c, _ = make(rule=Stub("rule", msg=AgentMessage.fail("x", "rule", "thiếu ngưỡng")))
    r = c.handle(RAW)
    assert r["status"] == "partial" and r["rules"] is None
    assert r["prediction"] is not None


def test_exception_inside_agent_is_caught_and_traced():
    c, _ = make(dl=Stub("dl", exc=RuntimeError("bùm")))
    r = c.handle(RAW)
    assert r["status"] == "partial"
    dl_trace = [t for t in r["trace"] if t["agent"] == "dl"][0]
    assert dl_trace["status"] == "error"
    assert any("bùm" in e["error"] for e in r["errors"])


def test_non_message_return_value_is_error_not_crash():
    class Bad:
        def run(self, rid, *a): return {"not": "a message"}
    c = CoordinatorAgent(Stub("data", {"features": {}}), Bad(), Stub("rule"), Stub("kg"), new_id=lambda: "r1")
    r = c.handle(RAW)
    assert r["status"] == "partial"
    assert any("AgentMessage" in e["error"] for e in r["errors"])


def test_request_id_is_shared_by_all_agents_and_result():
    c, a = make()
    r = c.handle(RAW)
    assert r["request_id"] == "req_fixed"
    for name in ("data", "dl", "rule", "kg"):
        assert all(call[0] == "req_fixed" for call in a[name].calls)


def test_trace_has_every_step_and_skipped_explain():
    c, _ = make()
    r = c.handle(RAW)
    names = [t["agent"] for t in r["trace"]]
    assert names == ["data", "dl", "rule", "kg", "explain"]
    assert r["trace"][-1]["status"] == "skipped"
    assert all(isinstance(t["ms"], int) and t["ms"] >= 0 for t in r["trace"])


def test_explainer_output_becomes_report():
    exp = Stub("explain", {"report": "BÁO CÁO"})
    c, _ = make(explainer=exp)
    r = c.handle(RAW)
    assert r["report"] == "BÁO CÁO" and r["status"] == "ok"
    outputs = exp.calls[0][1]
    assert set(outputs) == {"prediction", "rules", "knowledge"}


def test_explainer_failure_makes_partial_without_report():
    c, _ = make(explainer=Stub("explain", msg=AgentMessage.fail("x", "explain", "lỗi mẫu")))
    r = c.handle(RAW)
    assert r["status"] == "partial" and r["report"] is None


def test_monitor_receives_trace_once():
    seen = []
    class Mon:
        def record(self, rid, trace, outcome): seen.append((rid, len(trace), outcome))
    c, _ = make(monitor=Mon())
    c.handle(RAW)
    assert seen == [("req_fixed", 5, "ok")]   # 4 agent + bước explain bị bỏ qua
    assert len(seen) == 1


def test_monitor_failure_does_not_break_result():
    class Mon:
        def record(self, rid, trace, outcome): raise IOError("đĩa đầy")
    c, _ = make(monitor=Mon())
    r = c.handle(RAW)
    assert r["status"] == "ok" and r["prediction"] is not None
    assert any(e["agent"] == "monitor" for e in r["errors"])


def test_default_question_forwarded_to_kg_and_custom_overrides():
    c, a = make()
    c.handle(RAW)
    assert a["kg"].calls[-1][1] == DEFAULT_QUESTION
    c.handle(RAW, "Triệu chứng là gì?")
    assert a["kg"].calls[-1][1] == "Triệu chứng là gì?"


def test_outputs_keep_prediction_rules_evidence_separate():
    c, _ = make()
    r = c.handle(RAW)
    assert isinstance(r["prediction"], dict) and isinstance(r["rules"], dict) and isinstance(r["evidence"], list)
    assert "label" in r["prediction"] and "flags" in r["rules"]


def test_default_id_format():
    c = CoordinatorAgent(Stub("data", {"features": {}}), Stub("dl"), Stub("rule"), Stub("kg"))
    rid = c.handle(RAW)["request_id"]
    assert rid.startswith("req_") and len(rid) == 12


def test_handle_chat_only_invokes_kg():
    c, a = make()
    res = c.handle_chat("tiểu đường tuýp 2")
    assert ORDER == ["kg"]
    assert res["status"] == "ok"
    assert res["request_id"].startswith("chat_")
    assert res["has_patient_context"] is False
    assert "bằng chứng" in res["answer"]


def test_handle_chat_with_patient_context():
    c, a = make()
    ctx = {"age": 50, "HbA1c_level": 7.0, "risk_label": "nguy cơ cao"}
    res = c.handle_chat("chế độ ăn", context=ctx)
    assert ORDER == ["kg"]
    assert res["status"] == "ok"
    assert res["has_patient_context"] is True
    assert "Hồ sơ bệnh nhân ghi nhận" in res["answer"]
    assert "HbA1c: 7.0%" in res["answer"]

