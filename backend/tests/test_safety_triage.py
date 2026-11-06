from validators.safety_triage import triage


def test_self_harm_is_crisis():
    assert triage("Tôi muốn chết vì bệnh tiểu đường")["level"] == "crisis"


def test_low_glucose_number_triggers():
    out = triage("Đường huyết của tôi 55 mg/dL và tôi đang run")
    assert out["level"] == "emergency_low_glucose"


def test_glucose_at_70_does_not_trigger_numeric_rule():
    assert triage("Đường huyết lúc đói 70 mg/dL có sao không?") is None


def test_hypoglycemia_word_boundary_avoids_false_emergency_match():
    # "trung" must not match "run"; known hypoglycemia still gets an info alert.
    out = triage("Tôi bị hạ đường huyết và đang ở trung tâm y tế")
    assert out["level"] == "low_glucose_info"
    assert out["level"] != "emergency_low_glucose"


def test_emergency_symptom_with_diabetes_context():
    assert triage("Bị tiểu đường mà tôi ngất xỉu")["level"] == "emergency"


def test_normal_question_passes_through():
    assert triage("Triệu chứng tiểu đường là gì?") is None


def test_insulin_dose_question_is_referred_to_clinician():
    out = triage("Người mới bị tiểu đường nên tiêm insulin bao nhiêu đơn vị?")

    assert out["level"] == "medication_dose"
    assert "bác sĩ" in out["message"]
    assert "không thể xác định liều insulin" in out["message"]