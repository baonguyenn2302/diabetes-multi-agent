import pytest

from agents.risk_assessment_agent import RiskAssessmentAgent
from services.model_service import ModelService, ModelUnavailableError
from validators.health_input import validate_health_input

VALID = {
    "gender": "Female",
    "smoking_history": "never",
    "age": 45,
    "hypertension": 0,
    "heart_disease": 0,
    "bmi": 26.5,
    "HbA1c_level": 5.8,
    "blood_glucose_level": 120,
}

MINI_METADATA = {
    "input_fields": list(VALID.keys()),
    "categorical_values": {
        "gender": ["Female", "Male", "Other"],
        "smoking_history": ["No Info", "current", "ever", "former", "never", "not current"],
    },
    "numeric_ranges": {
        "age": [18.0, 80.0],
        "hypertension": [0.0, 1.0],
        "heart_disease": [0.0, 1.0],
        "bmi": [10.01, 91.82],
        "HbA1c_level": [3.5, 9.0],
        "blood_glucose_level": [80.0, 300.0],
    },
    "units": {"age": "năm", "bmi": "kg/m2"},
}


def make_task(features):
    return {
        "session_id": "s1",
        "task_id": "t1",
        "task": "estimate_diabetes_risk",
        "input": {"features": features},
    }


# ---------- Validator: không cần model ----------

def test_validator_success():
    out = validate_health_input(VALID, MINI_METADATA)
    assert out["status"] == "success"
    assert out["clean_features"]["age"] == 45.0


def test_validator_missing_field():
    features = {k: v for k, v in VALID.items() if k != "bmi"}
    out = validate_health_input(features, MINI_METADATA)
    assert out["status"] == "needs_input"
    assert out["missing_fields"] == ["bmi"]


def test_validator_rejects_underage():
    out = validate_health_input({**VALID, "age": 15}, MINI_METADATA)
    assert out["status"] == "invalid_input"
    assert "age" in out["errors"]


def test_validator_rejects_unknown_category():
    out = validate_health_input({**VALID, "smoking_history": "sometimes"}, MINI_METADATA)
    assert out["status"] == "invalid_input"
    assert "smoking_history" in out["errors"]


def test_validator_rejects_non_binary_flag():
    out = validate_health_input({**VALID, "hypertension": 0.5}, MINI_METADATA)
    assert out["status"] == "invalid_input"
    assert "hypertension" in out["errors"]


def test_validator_rejects_out_of_range():
    out = validate_health_input({**VALID, "blood_glucose_level": 500}, MINI_METADATA)
    assert out["status"] == "invalid_input"
    assert "blood_glucose_level" in out["errors"]


# ---------- Agent: cần file model thật ----------

@pytest.fixture(scope="module")
def agent():
    service = ModelService()
    try:
        service.load()
    except ModelUnavailableError:
        pytest.skip("Chưa có file model trong models/")
    return RiskAssessmentAgent(service)


def test_agent_success(agent):
    out = agent.run(make_task(VALID))
    assert out["status"] == "success"
    assert out["error"] is None
    assert 0.0 <= out["result"]["probability"] <= 1.0
    assert out["result"]["prediction"] in (0, 1)


def test_agent_needs_input(agent):
    features = {k: v for k, v in VALID.items() if k != "bmi"}
    out = agent.run(make_task(features))
    assert out["status"] == "needs_input"
    assert out["result"]["missing_fields"] == ["bmi"]


def test_agent_invalid_input(agent):
    out = agent.run(make_task({**VALID, "age": 15}))
    assert out["status"] == "invalid_input"
    assert "age" in out["error"]["fields"]


def test_agent_does_not_predict_on_invalid_input(agent):
    out = agent.run(make_task({**VALID, "age": 15}))
    assert "probability" not in out["result"]


def test_agent_model_missing_returns_error(tmp_path):
    agent = RiskAssessmentAgent(ModelService(tmp_path))
    out = agent.run(make_task(VALID))
    assert out["status"] == "error"
    assert out["error"]["code"] == "model_unavailable"