"""Test Rule-Based Agent với ngưỡng lấy từ dữ liệu KB (không cần kết nối Neo4j)."""
import pathlib, sys
from app.agents.rule_agent import RuleBasedAgent, THRESHOLD_QUERY, thresholds_from_rows

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))
import build_kb as kb

ROWS = [{"test_id": a, "relation": t, "target_id": b,
         "min_value": p.get("min_value"), "max_value": p.get("max_value"),
         "criterion": p.get("criterion"), "source_id": s}
        for a, t, b, s, p in kb.RELS if t in ("DIAGNOSES", "INDICATES") and a.startswith("test_")]


def runner(cypher, params):
    assert cypher == THRESHOLD_QUERY
    return [dict(r) for r in ROWS]


AGENT = RuleBasedAgent.from_runner(runner)
BASE = dict(gender="Female", age=30, bmi=22.0, hypertension=0, heart_disease=0,
            smoking_history="never", HbA1c_level=5.0, blood_glucose_level=90.0)


def run(prediction=None, **kw):
    return AGENT.run("r", {**BASE, **kw}, prediction)


def ids(m):
    return [f["id"] for f in m.payload["flags"]]


def test_thresholds_loaded_from_kg_rows():
    th = thresholds_from_rows(ROWS)
    assert th["test_hba1c"]["diagnosis_min"] == 6.5
    assert th["test_hba1c"]["prediabetes_min"] == 5.7
    assert th["test_hba1c"]["prediabetes_max"] == 6.4
    assert th["test_fpg"]["prediabetes_max"] == 125.0
    assert th["test_rpg"]["diagnosis_min"] == 200.0


def test_hba1c_diabetes_boundary():
    assert "R01" in ids(run(HbA1c_level=6.5))
    m = run(HbA1c_level=6.4)
    assert "R02" in ids(m) and "R01" not in ids(m)


def test_hba1c_gap_between_6_4_and_6_5_is_prediabetes():
    assert "R02" in ids(run(HbA1c_level=6.45))


def test_hba1c_normal_has_no_lab_flag():
    assert not any(i in ids(run(HbA1c_level=5.5)) for i in ("R01", "R02"))


def test_glucose_levels():
    assert "R03" in ids(run(blood_glucose_level=210))
    assert "R04" in ids(run(blood_glucose_level=150))
    assert "R05" in ids(run(blood_glucose_level=110))
    assert not any(i in ids(run(blood_glucose_level=90)) for i in ("R03", "R04", "R05"))


def test_glucose_flags_are_mutually_exclusive():
    assert ids(run(blood_glucose_level=210)).count("R03") == 1
    assert "R04" not in ids(run(blood_glucose_level=210))


def test_risk_flags():
    got = ids(run(age=50, bmi=32.0, hypertension=1, heart_disease=1, smoking_history="former"))
    assert got == ["R06", "R07", "R08", "R09", "R10"]


def test_no_risk_flags_for_healthy_profile():
    assert ids(run()) == []


def test_conflict_model_low_but_lab_high_needs_review():
    m = run(prediction={"prediction": 0}, HbA1c_level=7.0)
    assert "C01" in ids(m) and m.payload["needs_human_review"] is True


def test_conflict_model_high_but_labs_normal_needs_review():
    m = run(prediction={"prediction": 1})
    assert "C02" in ids(m) and m.payload["needs_human_review"] is True


def test_consistent_prediction_no_review():
    m = run(prediction={"prediction": 1}, HbA1c_level=7.0, blood_glucose_level=150)
    assert m.payload["needs_human_review"] is False and m.payload["conflicts"] == []


def test_no_model_prediction_means_no_conflict_check():
    m = run(prediction=None, HbA1c_level=7.0)
    assert m.payload["needs_human_review"] is False


def test_c02_requires_both_labs_present():
    m = AGENT.run("r", {**BASE, "blood_glucose_level": None, "HbA1c_level": 5.0}, {"prediction": 1})
    assert "C02" not in ids(m)


def test_every_flag_has_source_and_text():
    m = run(age=50, bmi=32.0, hypertension=1, heart_disease=1, smoking_history="current",
            HbA1c_level=6.8, blood_glucose_level=210, prediction={"prediction": 0})
    for f in m.payload["flags"]:
        assert f["source_id"] and f["text"] and f["level"] in ("high", "medium", "low", "review")


def test_no_medication_or_dosage_language():
    m = run(age=50, bmi=32.0, HbA1c_level=6.8, blood_glucose_level=210, prediction={"prediction": 0})
    text = " ".join(f["text"].lower() for f in m.payload["flags"])
    assert "liều" not in text and "kê đơn" not in text


def test_missing_kg_thresholds_return_error_not_exception():
    m = RuleBasedAgent.from_runner(lambda c, p: []).run("r", BASE, None)
    assert m.status == "error" and "Thiếu ngưỡng trong KG" in m.error


def test_runner_failure_raises_at_load_time():
    """Lỗi kết nối KG phải hiện rõ khi nạp ngưỡng, không âm thầm bỏ qua."""
    def broken(c, p): raise ConnectionError("mất kết nối")
    try:
        RuleBasedAgent.from_runner(broken)
        raise AssertionError("phải ném lỗi khi kết nối hỏng")
    except ConnectionError:
        pass


def test_agent_with_no_thresholds_returns_error_message():
    m = RuleBasedAgent({}).run("r", BASE, None)
    assert m.status == "error" and "Thiếu ngưỡng" in m.error
