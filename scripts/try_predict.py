"""Chạy thử DL Agent với vài bệnh nhân mẫu.  python scripts/try_predict.py"""
import json, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from app.agents.dl_agent import DLPredictionAgent

SAMPLES = {
    "Khỏe mạnh (kỳ vọng: nguy cơ thấp)": dict(
        gender="Female", age=25, hypertension=0, heart_disease=0,
        smoking_history="never", bmi=22.0, HbA1c_level=5.0, blood_glucose_level=100),
    "Nguy cơ cao (kỳ vọng: nguy cơ cao)": dict(
        gender="Male", age=62, hypertension=1, heart_disease=1,
        smoking_history="former", bmi=33.5, HbA1c_level=8.2, blood_glucose_level=220),
    "Thiếu feature (kỳ vọng: status=error)": dict(gender="Male", age=40),
}

agent = DLPredictionAgent.from_paths()
for name, feats in SAMPLES.items():
    msg = agent.run("req_try", feats)
    print(f"\n=== {name}")
    print(json.dumps(msg.model_dump(), indent=2, ensure_ascii=False))
