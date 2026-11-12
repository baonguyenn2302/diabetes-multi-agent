"""Định nghĩa feature của dataset diabetes_prediction_dataset.csv.

Dùng chung cho: huấn luyện model, DL Agent, và (giai đoạn 3) Patient Data Agent.
"""

# Thứ tự cột như trong file CSV
FEATURE_NAMES = [
    "gender", "age", "hypertension", "heart_disease",
    "smoking_history", "bmi", "HbA1c_level", "blood_glucose_level",
]
TARGET = "diabetes"

NUMERIC_FEATURES = ["age", "bmi", "HbA1c_level", "blood_glucose_level"]
BINARY_FEATURES = ["hypertension", "heart_disease"]          # 0 / 1
CATEGORICAL_FEATURES = ["gender", "smoking_history"]

ALLOWED_CATEGORIES = {
    "gender": ["Female", "Male", "Other"],
    "smoking_history": ["never", "No Info", "current", "former", "not current", "ever"],
}

# Khoảng giá trị hợp lý (dùng cho Data Agent ở giai đoạn 3)
VALUE_RANGES = {
    "age": (0, 120),
    "bmi": (10, 100),
    "HbA1c_level": (3, 15),
    "blood_glucose_level": (40, 600),
}
