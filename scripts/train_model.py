"""Huấn luyện model Deep Learning (Keras) dự đoán nguy cơ tiểu đường.

Chạy (tại thư mục gốc project):
    python scripts/train_model.py
    python scripts/train_model.py --epochs 30

Đầu ra trong models/:
    model.keras, preprocessor.joblib, model_meta.json, model_card.md
"""
import argparse, json, sys, datetime, pathlib

import numpy as np
import pandas as pd
import joblib
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                             f1_score, roc_auc_score, confusion_matrix)

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from app.features import (FEATURE_NAMES, TARGET, NUMERIC_FEATURES,
                          BINARY_FEATURES, CATEGORICAL_FEATURES)

SEED = 42
MODEL_VERSION = "diabetes_dl_v1"


# ---------- 1. Dữ liệu ----------
def load_and_clean(csv_path):
    df = pd.read_csv(csv_path)
    n_raw = len(df)
    missing = [c for c in FEATURE_NAMES + [TARGET] if c not in df.columns]
    if missing:
        raise ValueError(f"CSV thiếu cột: {missing}")
    df = df.drop_duplicates().reset_index(drop=True)
    info = {"rows_raw": n_raw, "rows_after_dedup": len(df),
            "duplicates_removed": n_raw - len(df),
            "positive_rate": round(float(df[TARGET].mean()), 4)}
    return df, info


def build_preprocessor():
    return ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), NUMERIC_FEATURES),
            ("bin", "passthrough", BINARY_FEATURES),
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False),
             CATEGORICAL_FEATURES),
        ],
        sparse_threshold=0.0,
    )


def split_data(df):
    X, y = df[FEATURE_NAMES], df[TARGET].astype(int)
    X_tv, X_te, y_tv, y_te = train_test_split(
        X, y, test_size=0.15, stratify=y, random_state=SEED)
    X_tr, X_va, y_tr, y_va = train_test_split(
        X_tv, y_tv, test_size=0.15 / 0.85, stratify=y_tv, random_state=SEED)
    return X_tr, X_va, X_te, y_tr, y_va, y_te


# ---------- 2. Model Keras ----------
def keras_trainer(Xtr, ytr, Xva, yva, class_weight, epochs):
    from tensorflow import keras
    from tensorflow.keras import layers
    keras.utils.set_random_seed(SEED)

    model = keras.Sequential([
        keras.Input(shape=(Xtr.shape[1],)),
        layers.Dense(64, activation="relu"),
        layers.Dropout(0.3),
        layers.Dense(32, activation="relu"),
        layers.Dropout(0.2),
        layers.Dense(1, activation="sigmoid"),
    ])
    model.compile(optimizer=keras.optimizers.Adam(1e-3),
                  loss="binary_crossentropy",
                  metrics=["accuracy", keras.metrics.AUC(name="auc")])
    model.fit(Xtr, ytr, validation_data=(Xva, yva), epochs=epochs,
              batch_size=256, class_weight=class_weight, verbose=2,
              callbacks=[keras.callbacks.EarlyStopping(
                  monitor="val_auc", mode="max", patience=5,
                  restore_best_weights=True)])
    return model


# ---------- 3. Đánh giá ----------
def tune_threshold(y_true, scores):
    """Chọn ngưỡng cho F1 tốt nhất trên tập VALIDATION (không dùng tập test)."""
    best_t, best_f1 = 0.5, -1.0
    for t in np.arange(0.10, 0.91, 0.01):
        f1 = f1_score(y_true, (scores >= t).astype(int), zero_division=0)
        if f1 > best_f1:
            best_t, best_f1 = float(round(t, 2)), f1
    return best_t


def evaluate(y_true, scores, threshold):
    pred = (scores >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_true, pred).ravel()
    return {
        "threshold": threshold,
        "accuracy": round(accuracy_score(y_true, pred), 4),
        "precision": round(precision_score(y_true, pred, zero_division=0), 4),
        "recall": round(recall_score(y_true, pred), 4),
        "f1": round(f1_score(y_true, pred), 4),
        "roc_auc": round(roc_auc_score(y_true, scores), 4),
        "confusion_matrix": {"tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)},
    }


def write_model_card(path, meta):
    m, d = meta["metrics_test"], meta["dataset"]
    cm = m["confusion_matrix"]
    text = f"""# Model Card – {meta['model_version']}

> Prototype học tập. Điểm số/dự đoán KHÔNG phải chẩn đoán xác định và chưa được kiểm chứng lâm sàng.

- **Ngày tạo:** {meta['created_at']}
- **Bài toán:** phân loại nhị phân – dự đoán nguy cơ tiểu đường (`diabetes` = 1) hay không (0).
  Dataset không có nhãn loại 1 / loại 2 nên model **không** phân biệt loại tiểu đường.
- **Dataset:** `diabetes_prediction_dataset.csv` – {d['rows_raw']} dòng, loại {d['duplicates_removed']} dòng trùng
  → {d['rows_after_dedup']} dòng; tỉ lệ dương tính {d['positive_rate']}.
- **Chia dữ liệu:** train 70% / validation 15% / test 15% (stratified, seed {meta['seed']}).
- **Feature (đúng thứ tự):** {', '.join(meta['feature_names'])}
- **Tiền xử lý:** StandardScaler cho {', '.join(meta['numeric_features'])};
  giữ nguyên {', '.join(meta['binary_features'])};
  OneHotEncoder cho {', '.join(meta['categorical_features'])} (giá trị lạ → vector 0).
  Bộ tiền xử lý fit **chỉ trên tập train**, lưu ở `preprocessor.joblib`.
- **Kiến trúc:** Dense(64, ReLU) → Dropout(0.3) → Dense(32, ReLU) → Dropout(0.2) → Dense(1, sigmoid).
- **Huấn luyện:** Adam(1e-3), binary cross-entropy, batch 256, EarlyStopping theo val AUC,
  class_weight để bù mất cân bằng lớp.
- **Output:** xác suất `score` ∈ [0,1]; `prediction = 1` nếu `score ≥ {m['threshold']}`
  (ngưỡng chọn theo F1 trên tập validation).
- **Kết quả trên tập test:**

| Metric | Giá trị |
|---|---|
| Accuracy | {m['accuracy']} |
| Precision | {m['precision']} |
| Recall | {m['recall']} |
| F1 | {m['f1']} |
| ROC-AUC | {m['roc_auc']} |

  Confusion matrix: TN={cm['tn']}, FP={cm['fp']}, FN={cm['fn']}, TP={cm['tp']}.

## Hạn chế
- Dataset công khai, không rõ quy trình thu thập; chưa kiểm chứng lâm sàng.
- `HbA1c_level` và `blood_glucose_level` là các chỉ số gắn rất chặt với định nghĩa bệnh nên
  accuracy cao không đồng nghĩa với việc model đáng tin trong thực tế.
- Mất cân bằng lớp (chỉ ~{round(d['positive_rate']*100, 1)}% dương tính): nên nhìn Recall/Precision/AUC, không chỉ Accuracy.
- Model chưa được hiệu chỉnh xác suất (calibration): `score` không phải xác suất thật.
"""
    pathlib.Path(path).write_text(text, encoding="utf-8")


# ---------- 4. Pipeline ----------
def run(csv_path, out_dir, epochs=50, trainer=keras_trainer):
    out = pathlib.Path(out_dir); out.mkdir(parents=True, exist_ok=True)

    df, info = load_and_clean(csv_path)
    print(f"Dữ liệu: {info}")
    X_tr, X_va, X_te, y_tr, y_va, y_te = split_data(df)
    print(f"Train/Val/Test = {len(X_tr)}/{len(X_va)}/{len(X_te)}")

    pre = build_preprocessor().fit(X_tr)          # chỉ fit trên train
    Xtr, Xva, Xte = (pre.transform(a).astype("float32") for a in (X_tr, X_va, X_te))
    print(f"Số chiều đầu vào sau tiền xử lý: {Xtr.shape[1]}")

    n, n_pos = len(y_tr), int(y_tr.sum())
    class_weight = {0: n / (2 * (n - n_pos)), 1: n / (2 * n_pos)}

    model = trainer(Xtr, y_tr.values, Xva, y_va.values, class_weight, epochs)

    s_va = np.asarray(model.predict(Xva, verbose=0)).ravel()
    s_te = np.asarray(model.predict(Xte, verbose=0)).ravel()
    thr = tune_threshold(y_va.values, s_va)
    metrics = evaluate(y_te.values, s_te, thr)
    print("Kết quả TEST:", json.dumps(metrics, indent=2))

    model.save(out / "model.keras")
    joblib.dump(pre, out / "preprocessor.joblib")

    cat_enc = pre.named_transformers_["cat"]
    meta = {
        "model_version": MODEL_VERSION,
        "created_at": datetime.datetime.now().isoformat(timespec="seconds"),
        "seed": SEED,
        "feature_names": FEATURE_NAMES,
        "numeric_features": NUMERIC_FEATURES,
        "binary_features": BINARY_FEATURES,
        "categorical_features": CATEGORICAL_FEATURES,
        "categories": {f: [str(c) for c in cats] for f, cats in
                       zip(CATEGORICAL_FEATURES, cat_enc.categories_)},
        "threshold": thr,
        "labels": {"0": "nguy cơ thấp", "1": "nguy cơ cao"},
        "metrics_test": metrics,
        "dataset": info,
    }
    (out / "model_meta.json").write_text(
        json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    write_model_card(out / "model_card.md", meta)
    print(f"\nĐã lưu model + preprocessor + meta + model_card vào: {out}")
    return meta


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=str(ROOT / "data" / "diabetes_prediction_dataset.csv"))
    ap.add_argument("--out", default=str(ROOT / "models"))
    ap.add_argument("--epochs", type=int, default=50)
    a = ap.parse_args()
    if not pathlib.Path(a.data).exists():
        sys.exit(f"Không tìm thấy file dữ liệu: {a.data}\n"
                 "-> Đặt diabetes_prediction_dataset.csv vào thư mục data/")
    run(a.data, a.out, a.epochs)
