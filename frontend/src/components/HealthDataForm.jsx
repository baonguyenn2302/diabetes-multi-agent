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

// step="any" cho số thập phân: tránh lỗi "giá trị gần nhất hợp lệ" của trình duyệt
// (trình duyệt tính bước nhảy từ min, nên 22 không hợp lệ khi min = 10.01 và step = 0.1)
const NUMERIC_FIELDS = [
  { key: "age", label: "Tuổi (năm)", min: 18, max: 80, step: 1, unit: "năm" },
  {
    key: "bmi",
    label: "BMI (kg/m²)",
    min: 10.01,
    max: 91.82,
    step: "any",
    unit: "kg/m²",
  },
  {
    key: "HbA1c_level",
    label: "HbA1c (%)",
    min: 3.5,
    max: 9.0,
    step: "any",
    unit: "%",
  },
  {
    key: "blood_glucose_level",
    label: "Đường huyết (mg/dL)",
    min: 80,
    max: 300,
    step: 1,
    unit: "mg/dL",
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

function rangeError(field, raw) {
  if (raw === "") return null;
  const n = Number(raw);
  if (Number.isNaN(n)) return "Phải là số";
  if (n < field.min || n > field.max) {
    return `Ngoài khoảng ${field.min} – ${field.max} ${field.unit}`;
  }
  return null;
}

export default function HealthDataForm({ onSubmit, disabled }) {
  const [values, setValues] = useState(EMPTY);

  function update(key, value) {
    setValues((prev) => ({ ...prev, [key]: value }));
  }

  const errors = Object.fromEntries(
    NUMERIC_FIELDS.map((f) => [f.key, rangeError(f, values[f.key])]).filter(
      ([, e]) => e,
    ),
  );
  const complete = Object.values(values).every((v) => v !== "");
  const canSubmit = complete && Object.keys(errors).length === 0 && !disabled;

  function handleSubmit(e) {
    e.preventDefault();
    if (!canSubmit) return;
    const numericKeys = new Set([
      ...NUMERIC_FIELDS.map((f) => f.key),
      ...BINARY_FIELDS.map((f) => f.key),
    ]);
    const features = Object.fromEntries(
      Object.entries(values).map(([k, v]) => [
        k,
        numericKeys.has(k) ? Number(v) : v,
      ]),
    );
    onSubmit(features);
  }

  return (
    <form onSubmit={handleSubmit} className="health-form" noValidate>
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
          <small>
            Khoảng hợp lệ: {f.min} – {f.max} {f.unit}
          </small>
          {errors[f.key] && (
            <span className="field-error">{errors[f.key]}</span>
          )}
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

      <button type="submit" disabled={!canSubmit}>
        Đánh giá nguy cơ
      </button>
    </form>
  );
}
