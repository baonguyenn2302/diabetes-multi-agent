"""DL Prediction Agent: bọc model Keras đã train thành một agent.

Input : dict features thô (đúng tên feature trong app/features.py)
Output: AgentMessage(payload={prediction, label, score, threshold})
Agent không ném lỗi ra ngoài: mọi lỗi trả về status="error".
"""
import json
import numpy as np
import pandas as pd

from app.schemas import AgentMessage
from app.config import settings, resolve_path


class DLPredictionAgent:
    NAME = "DiabetesPredictionAgent"

    def __init__(self, model, preprocessor, meta: dict):
        self.model = model
        self.preprocessor = preprocessor
        self.meta = meta
        self.features = meta["feature_names"]
        self.threshold = float(meta.get("threshold", 0.5))
        self.labels = {int(k): v for k, v in meta.get("labels", {}).items()} or \
                      {0: "nguy cơ thấp", 1: "nguy cơ cao"}
        self.version = meta.get("model_version", "unknown")

    @classmethod
    def from_paths(cls, model_path=None, preprocessor_path=None, meta_path=None):
        """Nạp model/preprocessor/meta từ đĩa (cần TensorFlow)."""
        import joblib
        from tensorflow import keras
        model = keras.models.load_model(resolve_path(model_path or settings.model_path))
        pre = joblib.load(resolve_path(preprocessor_path or settings.preprocessor_path))
        meta = json.loads(resolve_path(meta_path or settings.meta_path)
                          .read_text(encoding="utf-8"))
        return cls(model, pre, meta)

    def run(self, request_id: str, features: dict) -> AgentMessage:
        try:
            missing = [f for f in self.features if f not in features]
            if missing:
                return AgentMessage.fail(request_id, self.NAME,
                                         f"Thiếu feature: {missing}", self.version)
            df = pd.DataFrame([{f: features[f] for f in self.features}],
                              columns=self.features)
            x = np.asarray(self.preprocessor.transform(df), dtype="float32")
            score = float(np.asarray(self.model.predict(x, verbose=0)).ravel()[0])
            pred = int(score >= self.threshold)
            return AgentMessage.ok(
                request_id, self.NAME,
                payload={"prediction": pred,
                         "label": self.labels[pred],
                         "score": round(score, 4),
                         "threshold": self.threshold,
                         "task": "binary: nguy cơ tiểu đường (có/không)"},
                version=self.version)
        except Exception as e:  # failure awareness: không giấu lỗi, không làm sập hệ thống
            return AgentMessage.fail(request_id, self.NAME,
                                     f"{type(e).__name__}: {e}", self.version)
