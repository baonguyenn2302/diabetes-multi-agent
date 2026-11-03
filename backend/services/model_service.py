"""Tải model Keras, preprocessor và metadata; cung cấp hàm dự đoán.

Chỉ là lớp hạ tầng: không chứa logic Agent và không diễn giải kết quả y khoa.
"""
from __future__ import annotations

import json
import logging
import pickle
from pathlib import Path
from typing import Any

import pandas as pd
import sklearn

logger = logging.getLogger(__name__)

# backend/services/model_service.py -> parents[2] là thư mục gốc của repo
DEFAULT_MODEL_DIR = Path(__file__).resolve().parents[2] / "models"


class ModelUnavailableError(RuntimeError):
    """Model hoặc file phụ trợ không tải được."""


class ModelService:
    def __init__(self, model_dir: str | Path = DEFAULT_MODEL_DIR):
        self.model_dir = Path(model_dir)
        self.metadata: dict[str, Any] | None = None
        self._model: Any = None
        self._preprocessor: Any = None

    @property
    def is_loaded(self) -> bool:
        return self._model is not None

    def load(self) -> None:
        """Tải một lần. Ném ModelUnavailableError nếu thiếu file hoặc lỗi."""
        if self.is_loaded:
            return
        try:
            with open(self.model_dir / "model_metadata.json", encoding="utf-8") as f:
                self.metadata = json.load(f)
            with open(self.model_dir / "preprocessor.pkl", "rb") as f:
                self._preprocessor = pickle.load(f)

            from tensorflow import keras  # import muộn để khởi động nhanh hơn

            self._model = keras.models.load_model(
                str(self.model_dir / self.metadata["model_file"])
            )
        except FileNotFoundError as exc:
            raise ModelUnavailableError(f"Thiếu file: {exc.filename}") from exc
        except Exception as exc:
            raise ModelUnavailableError(f"Không load được model: {exc}") from exc

        trained_with = self.metadata.get("versions", {}).get("scikit_learn")
        if trained_with and trained_with != sklearn.__version__:
            logger.warning(
                "scikit-learn đang dùng %s, khác bản lúc huấn luyện %s",
                sklearn.__version__,
                trained_with,
            )

    def health(self) -> dict[str, str]:
        try:
            self.load()
            return {"status": "ok", "detail": "Model đã sẵn sàng"}
        except ModelUnavailableError as exc:
            return {"status": "unavailable", "detail": str(exc)}

    def predict_probability(self, clean_features: dict[str, Any]) -> float:
        """Nhận dict đã qua validator, trả xác suất lớp dương (0..1)."""
        self.load()
        row = pd.DataFrame([clean_features], columns=self.metadata["input_fields"])
        x = self._preprocessor.transform(row)
        prob = self._model.predict(x, verbose=0)
        return float(prob.ravel()[0])