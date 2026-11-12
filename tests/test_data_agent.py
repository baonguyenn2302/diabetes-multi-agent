"""Test Patient Data Agent (không cần Neo4j, không cần TensorFlow)."""
import math
from app.agents.data_agent import PatientDataAgent

GOOD = dict(gender="Female", age=40, hypertension=0, heart_disease=0,
            smoking_history="never", bmi=25.0, HbA1c_level=5.5, blood_glucose_level=120)
AG = PatientDataAgent()


def test_valid_input_is_ok_and_typed():
    m = AG.run("r", GOOD)
    assert m.status == "ok", m.error
    f = m.payload["features"]
    assert isinstance(f["age"], float) and f["age"] == 40.0
    assert f["gender"] == "Female" and f["hypertension"] == 0
    assert m.payload["ignored_fields"] == []


def test_missing_feature_is_reported():
    d = {k: v for k, v in GOOD.items() if k != "bmi"}
    m = AG.run("r", d)
    assert m.status == "error" and "Thiếu feature: bmi" in m.error


def test_none_or_blank_counts_as_missing():
    assert "Thiếu feature: age" in AG.run("r", {**GOOD, "age": None}).error
    assert "Thiếu feature: gender" in AG.run("r", {**GOOD, "gender": "  "}).error


def test_non_numeric_value_rejected():
    m = AG.run("r", {**GOOD, "bmi": "abc"})
    assert m.status == "error" and "bmi phải là số" in m.error


def test_numeric_string_accepted_and_comma_decimal():
    m = AG.run("r", {**GOOD, "HbA1c_level": "5,8"})
    assert m.status == "ok" and m.payload["features"]["HbA1c_level"] == 5.8


def test_out_of_range_rejected():
    m = AG.run("r", {**GOOD, "HbA1c_level": 20})
    assert m.status == "error" and "ngoài khoảng" in m.error


def test_nan_and_inf_rejected():
    assert AG.run("r", {**GOOD, "bmi": float("nan")}).status == "error"
    assert AG.run("r", {**GOOD, "blood_glucose_level": float("inf")}).status == "error"


def test_invalid_category_rejected():
    m = AG.run("r", {**GOOD, "gender": "Unknown"})
    assert m.status == "error" and "gender" in m.error


def test_category_is_case_insensitive_and_canonicalized():
    m = AG.run("r", {**GOOD, "gender": "female", "smoking_history": "NO INFO"})
    assert m.status == "ok"
    assert m.payload["features"]["gender"] == "Female"
    assert m.payload["features"]["smoking_history"] == "No Info"


def test_binary_must_be_0_or_1():
    assert AG.run("r", {**GOOD, "hypertension": 2}).status == "error"
    assert AG.run("r", {**GOOD, "heart_disease": 0.5}).status == "error"
    assert AG.run("r", {**GOOD, "hypertension": True}).status == "error"


def test_extra_fields_are_ignored_and_listed():
    m = AG.run("r", {**GOOD, "note": "abc"})
    assert m.status == "ok" and m.payload["ignored_fields"] == ["note"]
    assert "note" not in m.payload["features"]


def test_non_dict_input_returns_error():
    m = AG.run("r", ["not", "a", "dict"])
    assert m.status == "error" and "dict" in m.error


def test_errors_are_listed_in_payload():
    m = AG.run("r", {**GOOD, "bmi": "x", "age": 200})
    assert m.status == "error" and len(m.payload["errors"]) == 2
