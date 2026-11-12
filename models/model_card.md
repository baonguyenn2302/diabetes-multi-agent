# Model Card – diabetes_dl_v1

> Prototype học tập. Điểm số/dự đoán KHÔNG phải chẩn đoán xác định và chưa được kiểm chứng lâm sàng.

- **Ngày tạo:** 2026-11-12T20:33:43
- **Bài toán:** phân loại nhị phân – dự đoán nguy cơ tiểu đường (`diabetes` = 1) hay không (0).
  Dataset không có nhãn loại 1 / loại 2 nên model **không** phân biệt loại tiểu đường.
- **Dataset:** `diabetes_prediction_dataset.csv` – 100000 dòng, loại 3854 dòng trùng
  → 96146 dòng; tỉ lệ dương tính 0.0882.
- **Chia dữ liệu:** train 70% / validation 15% / test 15% (stratified, seed 42).
- **Feature (đúng thứ tự):** gender, age, hypertension, heart_disease, smoking_history, bmi, HbA1c_level, blood_glucose_level
- **Tiền xử lý:** StandardScaler cho age, bmi, HbA1c_level, blood_glucose_level;
  giữ nguyên hypertension, heart_disease;
  OneHotEncoder cho gender, smoking_history (giá trị lạ → vector 0).
  Bộ tiền xử lý fit **chỉ trên tập train**, lưu ở `preprocessor.joblib`.
- **Kiến trúc:** Dense(64, ReLU) → Dropout(0.3) → Dense(32, ReLU) → Dropout(0.2) → Dense(1, sigmoid).
- **Huấn luyện:** Adam(1e-3), binary cross-entropy, batch 256, EarlyStopping theo val AUC,
  class_weight để bù mất cân bằng lớp.
- **Output:** xác suất `score` ∈ [0,1]; `prediction = 1` nếu `score ≥ 0.85`
  (ngưỡng chọn theo F1 trên tập validation).
- **Kết quả trên tập test:**

| Metric | Giá trị |
|---|---|
| Accuracy | 0.97 |
| Precision | 0.933 |
| Recall | 0.7115 |
| F1 | 0.8073 |
| ROC-AUC | 0.9749 |

  Confusion matrix: TN=13085, FP=65, FN=367, TP=905.

## Hạn chế
- Dataset công khai, không rõ quy trình thu thập; chưa kiểm chứng lâm sàng.
- `HbA1c_level` và `blood_glucose_level` là các chỉ số gắn rất chặt với định nghĩa bệnh nên
  accuracy cao không đồng nghĩa với việc model đáng tin trong thực tế.
- Mất cân bằng lớp (chỉ ~8.8% dương tính): nên nhìn Recall/Precision/AUC, không chỉ Accuracy.
- Model chưa được hiệu chỉnh xác suất (calibration): `score` không phải xác suất thật.
