"""Test Monitoring Agent: ghi log, đọc, thống kê. Dùng thư mục tạm, không đụng logs/ thật."""
import json, pathlib, tempfile, threading
from app.agents.monitoring_agent import MonitoringAgent, percentile


def _path():
    return pathlib.Path(tempfile.mkdtemp()) / "audit.jsonl"


def _trace(ms=(10, 20, 30, 40), status=("ok", "ok", "ok", "ok")):
    names = ["data", "dl", "rule", "kg"]
    return [{"agent": n, "status": s, "ms": m, "version": f"{n}_v1"} for n, m, s in zip(names, ms, status)]


def test_record_writes_one_json_line_with_core_fields():
    p = _path(); m = MonitoringAgent(p)
    m.record("req_1", _trace(), "ok")
    lines = p.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    rec = json.loads(lines[0])
    for k in ("ts", "request_id", "outcome", "total_ms", "steps", "agent_ms", "agents_failed", "versions"):
        assert k in rec, k
    assert rec["request_id"] == "req_1" and rec["outcome"] == "ok"


def test_total_ms_is_sum_of_steps():
    rec = MonitoringAgent(_path()).record("r", _trace(ms=(1, 2, 3, 4)), "ok")
    assert rec["total_ms"] == 10


def test_failed_agents_listed():
    rec = MonitoringAgent(_path()).record("r", _trace(status=("ok", "error", "ok", "ok")), "partial")
    assert rec["agents_failed"] == ["dl"]


def test_versions_collected_per_agent():
    rec = MonitoringAgent(_path()).record("r", _trace(), "ok")
    assert rec["versions"]["dl"] == "dl_v1" and len(rec["versions"]) == 4


def test_appends_in_order():
    p = _path(); m = MonitoringAgent(p)
    for i in range(3):
        m.record(f"req_{i}", _trace(), "ok")
    ids = [json.loads(l)["request_id"] for l in p.read_text(encoding="utf-8").splitlines()]
    assert ids == ["req_0", "req_1", "req_2"]


def test_io_error_does_not_raise_and_is_counted():
    blocker = _path(); blocker.write_text("tôi là file, không phải thư mục")
    m = MonitoringAgent(blocker / "audit.jsonl")
    rec = m.record("r", _trace(), "ok")
    assert rec["write_ok"] is False and m.write_errors == 1


def test_concurrent_writes_stay_valid_json():
    p = _path(); m = MonitoringAgent(p)
    threads = [threading.Thread(target=m.record, args=(f"req_{i}", _trace(), "ok")) for i in range(20)]
    for t in threads: t.start()
    for t in threads: t.join()
    recs, bad = m.read_records()
    assert bad == 0 and len(recs) == 20


def test_summary_counts_outcomes_and_percentiles():
    p = _path(); m = MonitoringAgent(p)
    for ms in range(1, 11):                 # total_ms = 4*ms
        m.record("r", _trace(ms=(ms, ms, ms, ms)), "ok")
    m.record("v", [{"agent": "data", "status": "error", "ms": 1}], "validation_error")
    s = m.summary()
    assert s["n_requests"] == 11
    assert s["outcomes"] == {"ok": 10, "validation_error": 1}
    assert s["total_ms"]["p50"] == 20          # 5 * 4
    assert s["total_ms"]["p95"] == 40          # 10 * 4; validation_error không tính vào tổng thời gian


def test_summary_agent_error_rate():
    p = _path(); m = MonitoringAgent(p)
    m.record("a", _trace(status=("ok", "error", "ok", "ok")), "partial")
    m.record("b", _trace(status=("ok", "ok", "ok", "ok")), "ok")
    s = m.summary()
    assert s["agents"]["dl"]["calls"] == 2 and s["agents"]["dl"]["error_rate"] == 0.5
    assert s["agents"]["data"]["error_rate"] == 0.0


def test_skipped_steps_do_not_count_in_agent_stats():
    p = _path(); m = MonitoringAgent(p)
    tr = _trace() + [{"agent": "explain", "status": "skipped", "ms": 0, "version": None}]
    m.record("r", tr, "ok")
    assert "explain" not in m.summary()["agents"]


def test_malformed_lines_are_skipped_and_counted():
    p = _path(); m = MonitoringAgent(p)
    m.record("r1", _trace(), "ok")
    with p.open("a", encoding="utf-8") as f:
        f.write("dòng rác không phải JSON\n\n")
    m.record("r2", _trace(), "ok")
    s = m.summary()
    assert s["n_requests"] == 2 and s["invalid_lines"] == 1


def test_summary_of_empty_log():
    s = MonitoringAgent(_path()).summary()
    assert s["n_requests"] == 0 and s["total_ms"] is None and s["agents"] == {}


def test_last_n_limits_summary():
    p = _path(); m = MonitoringAgent(p)
    for i in range(5):
        m.record(f"r{i}", _trace(), "ok")
    assert m.summary(last_n=2)["n_requests"] == 2


def test_percentile_nearest_rank():
    v = list(range(1, 11))
    assert percentile(v, 50) == 5 and percentile(v, 95) == 10
    assert percentile([], 50) is None
