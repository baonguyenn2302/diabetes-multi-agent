"""Unit test DL Agent bằng model GIẢ (không cần TensorFlow, không cần file model)."""
import numpy as np
import pandas as pd

from app.agents.dl_agent import DLPredictionAgent
from app.features import FEATURE_NAMES
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))
from train_model import build_preprocessor

GOOD = dict(gender="Female", age=40, hypertension=0, heart_disease=0,
            smoking_history="never", bmi=25.0, HbA1c_level=5.5, blood_glucose_level=120)


class FakeModel:
    """Trả về score cố định."""
    def __init__(self, score): self.score = score
    def predict(self, x, verbose=0): return np.full((len(x), 1), self.score)


class BrokenModel:
    def predict(self, x, verbose=0): raise RuntimeError("model hỏng")


def make_agent(model, threshold=0.5):
    df = pd.DataFrame([GOOD, {**GOOD, "gender": "Male", "age": 70,
                              "smoking_history": "current", "bmi": 31.0}])
    pre = build_preprocessor().fit(df[FEATURE_NAMES])
    meta = {"feature_names": FEATURE_NAMES, "threshold": threshold,
            "model_version": "test_v0"}
    return DLPredictionAgent(model, pre, meta)


def test_high_score_gives_positive_prediction():
    msg = make_agent(FakeModel(0.9)).run("r1", GOOD)
    assert msg.status == "ok" and msg.payload["prediction"] == 1
    assert msg.payload["label"] == "nguy cơ cao"
    assert msg.payload["score"] == 0.9 and msg.version == "test_v0"


def test_low_score_gives_negative_prediction():
    msg = make_agent(FakeModel(0.1)).run("r1", GOOD)
    assert msg.status == "ok" and msg.payload["prediction"] == 0


def test_threshold_is_respected():
    assert make_agent(FakeModel(0.4), threshold=0.3).run("r", GOOD).payload["prediction"] == 1
    assert make_agent(FakeModel(0.4), threshold=0.5).run("r", GOOD).payload["prediction"] == 0


def test_missing_feature_returns_error_not_exception():
    msg = make_agent(FakeModel(0.9)).run("r1", {"age": 40})
    assert msg.status == "error" and "Thiếu feature" in msg.error


def test_model_failure_returns_error_not_exception():
    msg = make_agent(BrokenModel()).run("r1", GOOD)
    assert msg.status == "error" and "model hỏng" in msg.error


def test_unknown_category_does_not_crash():
    msg = make_agent(FakeModel(0.5)).run("r1", {**GOOD, "smoking_history": "vape"})
    assert msg.status == "ok"
