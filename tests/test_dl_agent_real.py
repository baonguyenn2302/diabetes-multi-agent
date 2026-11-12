"""Test với model THẬT. Tự bỏ qua (skip) nếu chưa huấn luyện model."""
import pytest
from app.config import settings, resolve_path

HAVE_MODEL = all(resolve_path(p).exists() for p in
                 (settings.model_path, settings.preprocessor_path, settings.meta_path))
pytestmark = pytest.mark.skipif(not HAVE_MODEL, reason="Chưa có model: chạy scripts/train_model.py")

LOW = dict(gender="Female", age=25, hypertension=0, heart_disease=0,
           smoking_history="never", bmi=22.0, HbA1c_level=5.0, blood_glucose_level=100)
HIGH = dict(gender="Male", age=62, hypertension=1, heart_disease=1,
            smoking_history="former", bmi=33.5, HbA1c_level=8.2, blood_glucose_level=220)


def test_real_model_separates_low_and_high_risk():
    from app.agents.dl_agent import DLPredictionAgent
    agent = DLPredictionAgent.from_paths()
    low, high = agent.run("t", LOW), agent.run("t", HIGH)
    assert low.status == "ok" and high.status == "ok"
    assert 0.0 <= low.payload["score"] <= 1.0
    assert high.payload["score"] > low.payload["score"]
    assert low.payload["prediction"] == 0 and high.payload["prediction"] == 1
