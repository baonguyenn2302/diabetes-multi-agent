import json
import pickle
import random
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
import sklearn
import tensorflow as tf
from sklearn.compose import ColumnTransformer
from sklearn.metrics import f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from tensorflow import keras
from tensorflow.keras import layers

SEED = 42
random.seed(SEED)
np.random.seed(SEED)
tf.random.set_seed(SEED)

DATA_PATH = Path("data/raw/dataset.csv")
MODEL_DIR = Path("models")
MODEL_DIR.mkdir(exist_ok=True)

TARGET = "diabetes"
CATEGORICAL = ["gender", "smoking_history"]
NUMERIC = ["age", "hypertension", "heart_disease", "bmi", "HbA1c_level", "blood_glucose_level"]
FIELDS = CATEGORICAL + NUMERIC
THRESHOLD = 0.5

df = pd.read_csv(DATA_PATH)
df = df[df["age"] >= 18].copy()  # chỉ người trưởng thành
X = df[FIELDS]
y = df[TARGET].astype(int)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=SEED
)

# Preprocessor chỉ fit trên tập train
preprocessor = ColumnTransformer([
    ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), CATEGORICAL),
    ("num", StandardScaler(), NUMERIC),
])
X_train_p = preprocessor.fit_transform(X_train)
X_test_p = preprocessor.transform(X_test)
encoded_features = list(preprocessor.get_feature_names_out())

# Bù cho dữ liệu lệch lớp
n_pos = int(y_train.sum())
n_neg = len(y_train) - n_pos
class_weight = {0: 1.0, 1: n_neg / n_pos}

model = keras.Sequential([
    layers.Input(shape=(X_train_p.shape[1],)),
    layers.Dense(32, activation="relu"),
    layers.Dropout(0.2),
    layers.Dense(16, activation="relu"),
    layers.Dense(1, activation="sigmoid"),
])
model.compile(
    optimizer=keras.optimizers.Adam(1e-3),
    loss="binary_crossentropy",
    metrics=[keras.metrics.AUC(name="auc")],
)
model.fit(
    X_train_p, y_train,
    validation_split=0.2,
    epochs=100,
    batch_size=256,
    class_weight=class_weight,
    verbose=2,
    callbacks=[keras.callbacks.EarlyStopping(
        monitor="val_auc", mode="max", patience=10, restore_best_weights=True
    )],
)

probs = model.predict(X_test_p, verbose=0).ravel()
pred = (probs >= THRESHOLD).astype(int)
metrics = {
    "test_roc_auc": round(float(roc_auc_score(y_test, probs)), 3),
    "test_precision": round(float(precision_score(y_test, pred, zero_division=0)), 3),
    "test_recall": round(float(recall_score(y_test, pred)), 3),
    "test_f1": round(float(f1_score(y_test, pred)), 3),
    "threshold": THRESHOLD,
}

model.save(MODEL_DIR / "diabetes_mlp.keras")
with open(MODEL_DIR / "preprocessor.pkl", "wb") as f:
    pickle.dump(preprocessor, f)

metadata = {
    "model_file": "diabetes_mlp.keras",
    "preprocessor_file": "preprocessor.pkl",
    "target": TARGET,
    "input_fields": FIELDS,  # thứ tự cột đầu vào thô, validator dùng các trường này
    "categorical_values": {c: sorted(df[c].unique().tolist()) for c in CATEGORICAL},
    "numeric_ranges": {c: [float(df[c].min()), float(df[c].max())] for c in NUMERIC},
    "units": {
        "age": "năm",
        "bmi": "kg/m2",
        "HbA1c_level": "%",
        "blood_glucose_level": "mg/dL",
        "hypertension": "0/1",
        "heart_disease": "0/1",
    },
    "encoded_features": encoded_features,
    "dataset": {
        "file": "data/raw/dataset.csv",
        "rows_used": int(len(df)),
        "filter": "age >= 18",
        "source": "CẦN GHI NGUỒN CHÍNH XÁC",
    },
    "metrics": metrics,
    "versions": {
        "tensorflow": tf.__version__,
        "scikit_learn": sklearn.__version__,
        "python_trained_on": "3.13",
    },
    "trained_on": str(date.today()),
    "limitations": [
        "Dữ liệu huấn luyện không đại diện cho mọi nhóm dân cư, bao gồm người Việt Nam.",
        "Đơn vị các trường số là giả định, chưa được xác nhận từ nguồn dữ liệu.",
        "Kết quả chỉ là ước tính tham khảo, không phải chẩn đoán y khoa.",
    ],
}
with open(MODEL_DIR / "model_metadata.json", "w", encoding="utf-8") as f:
    json.dump(metadata, f, ensure_ascii=False, indent=2)

print(json.dumps(metrics, indent=2))