"""Test các hàm đánh giá thuần (không cần TensorFlow, Neo4j)."""
from app.evaluation import (ablation, group_of, kg_coverage, latency_summary, metrics, render_markdown,
                            rule_alert, same_metrics, select_cases)


def test_metrics_basic():
    m = metrics([1, 0, 1, 0], [1, 1, 0, 0])
    assert (m["tp"], m["fp"], m["fn"], m["tn"]) == (1, 1, 1, 1)
    assert m["precision"] == 0.5 and m["recall"] == 0.5 and m["f1"] == 0.5 and m["accuracy"] == 0.5


def test_metrics_no_positive_predictions_does_not_divide_by_zero():
    m = metrics([1, 1, 0], [0, 0, 0])
    assert m["precision"] == 0.0 and m["recall"] == 0.0 and m["f1"] == 0.0


def test_rule_alert_only_for_high_lab_flags():
    assert rule_alert([{"id": "R01"}]) is True
    assert rule_alert([{"id": "R03"}]) is True
    assert rule_alert([{"id": "R05"}, {"id": "R06"}]) is False
    assert rule_alert([]) is False


def test_ablation_counts_rescued_and_extra():
    y = [1, 1, 0]
    dl = [0, 1, 0]
    alert = [1, 0, 1]
    a = ablation(y, dl, alert)
    assert a["dl_only"]["recall"] == 0.5
    assert a["dl_plus_rule"]["recall"] == 1.0
    assert a["rescued_positives"] == 1
    assert a["extra_alerts_on_negatives"] == 1
    assert a["delta_recall"] == 0.5


def test_ablation_counts_review_flags():
    a = ablation([0, 1], [0, 1], [False, False], review=[True, False])
    assert a["review_flags"] == 1


def test_group_of():
    assert group_of(1, 1) == "TP" and group_of(1, 0) == "FN"
    assert group_of(0, 1) == "FP" and group_of(0, 0) == "TN"


def test_select_cases_only_contains_right_group_and_is_deterministic():
    rows = [{"idx": i, "y": i % 2, "dl": (i // 2) % 2, "score": 0.5, "alert": None} for i in range(40)]
    a = select_cases(rows, k=3, seed=7)
    b = select_cases(rows, k=3, seed=7)
    assert a == b
    for g, items in a.items():
        assert len(items) <= 3
        assert all(group_of(r["y"], r["dl"]) == g for r in items)


def test_latency_summary_skips_skipped_steps_and_computes_p95():
    traces = [[{"agent": "data", "status": "ok", "ms": 2},
               {"agent": "kg", "status": "ok", "ms": 100 + i},
               {"agent": "explain", "status": "skipped", "ms": 0}] for i in range(20)]
    s = latency_summary(traces)
    assert s["n"] == 20
    assert "explain" not in s["agents"]
    assert s["agents"]["kg"]["p95"] == 118
    assert s["total"]["p50"] == 2 + 109


def test_latency_summary_empty():
    assert latency_summary([])["total"] is None


def test_kg_coverage_counts_sourced_evidence():
    rows = [{"question": "q1", "evidence": [
                {"source_title": "WHO", "source_url": "https://x"},
                {"source_title": "Không rõ nguồn", "source_url": ""}]},
            {"question": "q2", "evidence": []}]
    c = kg_coverage(rows)
    assert c["total"] == 2 and c["sourced"] == 1 and c["share"] == 0.5
    assert c["items"][1]["n"] == 0


def test_same_metrics_tolerance():
    ref = {"accuracy": 0.97, "precision": 0.933, "recall": 0.7115, "f1": 0.8073, "roc_auc": 0.9749}
    assert same_metrics(dict(ref), ref)
    off = dict(ref, recall=0.72)
    assert not same_metrics(off, ref)


def test_render_markdown_has_sections_and_limits():
    d = {
        "model": {"metrics": {"accuracy": 0.97, "precision": 0.933, "recall": 0.7115, "f1": 0.8073, "roc_auc": 0.9749},
                  "card": {"accuracy": 0.97, "precision": 0.933, "recall": 0.7115, "f1": 0.8073, "roc_auc": 0.9749},
                  "matches_card": True, "n_test": 14422, "threshold": 0.85},
        "ablation": ablation([1, 0], [0, 0], [True, False], review=[False, False]),
        "rule_error": None,
        "cases": {"TP": [], "FN": [{"idx": 3, "y": 1, "score": 0.2, "dl": 0, "alert": True}],
                  "FP": [], "TN": []},
        "latency": latency_summary([[{"agent": "data", "status": "ok", "ms": 3}]]),
        "consistency": {"match": 1, "n": 1, "statuses": {"ok": 1}},
        "kg": kg_coverage([{"question": "q", "evidence": [{"source_title": "WHO", "source_url": "u"}]}]),
    }
    md = render_markdown(d)
    for h in ("## 1.", "## 2.", "## 3.", "## 4.", "## 5.", "## 6."):
        assert h in md
    assert "không phải bằng chứng lâm sàng" in md
    assert "Được cứu" not in md and "được cứu" in md


def test_render_markdown_handles_missing_rule_layer():
    d = {"model": {"metrics": {}, "card": {}, "matches_card": False, "n_test": 0, "threshold": 0.5},
         "ablation": None, "rule_error": "Neo4j không kết nối",
         "cases": {}, "latency": latency_summary([]), "consistency": {"match": 0, "n": 0},
         "kg": kg_coverage([])}
    md = render_markdown(d)
    assert "Không chạy được lớp Rule" in md and "Neo4j không kết nối" in md
