import { useState } from "react";

const CATEGORY_OPTIONS = {
  gender: ["Female", "Male", "Other"],
  smoking_history: [
    "No Info",
    "current",
    "ever",
    "former",
    "never",
    "not current",
  ],
};

const NUMERIC_FIELDS = [
  { key: "age", label: "Tuổi (năm)", min: 18, max: 80, step: 1 },
  { key: "bmi", label: "BMI (kg/m²)", min: 10.01, max: 91.82, step: 0.01 },
  { key: "HbA1c_level", label: "HbA1c (%)", min: 3.5, max: 9.0, step: 0.1 },
  {
    key: "blood_glucose_level",
    label: "Đường huyết (mg/dL)",
    min: 80,
    max: 300,
    step: 1,
  },
];

const BINARY_FIELDS = [
  { key: "hypertension", label: "Tăng huyết áp" },
  { key: "heart_disease", label: "Bệnh tim" },
];

const EMPTY = {
  gender: "",
  smoking_history: "",
  age: "",
  hypertension: "",
  heart_disease: "",
  bmi: "",
  HbA1c_level: "",
  blood_glucose_level: "",
};

export default function HealthDataForm({ onSubmit, disabled }) {
  const [values, setValues] = useState(EMPTY);

  function update(key, value) {
    setValues((prev) => ({ ...prev, [key]: value }));
  }

  function handleSubmit(e) {
    e.preventDefault();
    if (disabled) return;
    // Gửi chuỗi đã chuyển thành số. Backend vẫn là nơi kiểm tra cuối cùng.
    const features = Object.fromEntries(
      Object.entries(values).map(([k, v]) => [
        k,
        NUMERIC_FIELDS.some((f) => f.key === k) ||
          BINARY_FIELDS.some((f) => f.key === k)
          ? Number(v)
          : v,
      ]),
    );
    onSubmit(features);
  }

  const complete = Object.values(values).every((v) => v !== "");

  return (
    <form onSubmit={handleSubmit} className="health-form">
      <label>
        Giới tính
        <select
          value={values.gender}
          onChange={(e) => update("gender", e.target.value)}
        >
          <option value="">-- chọn --</option>
          {CATEGORY_OPTIONS.gender.map((o) => (
            <option key={o} value={o}>
              {o}
            </option>
          ))}
        </select>
      </label>

      <label>
        Tiền sử hút thuốc
        <select
          value={values.smoking_history}
          onChange={(e) => update("smoking_history", e.target.value)}
        >
          <option value="">-- chọn --</option>
          {CATEGORY_OPTIONS.smoking_history.map((o) => (
            <option key={o} value={o}>
              {o}
            </option>
          ))}
        </select>
      </label>

      {NUMERIC_FIELDS.map((f) => (
        <label key={f.key}>
          {f.label}
          <input
            type="number"
            min={f.min}
            max={f.max}
            step={f.step}
            value={values[f.key]}
            onChange={(e) => update(f.key, e.target.value)}
          />
        </label>
      ))}

      {BINARY_FIELDS.map((f) => (
        <label key={f.key}>
          {f.label}
          <select
            value={values[f.key]}
            onChange={(e) => update(f.key, e.target.value)}
          >
            <option value="">-- chọn --</option>
            <option value="0">Không</option>
            <option value="1">Có</option>
          </select>
        </label>
      ))}

      <button type="submit" disabled={disabled || !complete}>
        Đánh giá nguy cơ
      </button>
    </form>
  );
}
