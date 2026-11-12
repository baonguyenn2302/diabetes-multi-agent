"""Chạy thử toàn bộ luồng (Coordinator + 4 agent thật).   python scripts/try_coordinator.py"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from app.coordinator import build_default_coordinator

CASES = {
    "Khỏe mạnh": dict(gender="Female", age=25, hypertension=0, heart_disease=0, smoking_history="never",
                      bmi=22.0, HbA1c_level=5.0, blood_glucose_level=100),
    "Nguy cơ cao": dict(gender="Male", age=62, hypertension=1, heart_disease=1, smoking_history="former",
                        bmi=33.5, HbA1c_level=8.2, blood_glucose_level=220),
    "Dữ liệu sai": dict(gender="Male", age=40, bmi="abc"),
}

coord = build_default_coordinator()
try:
    for name, raw in CASES.items():
        r = coord.handle(raw, "Triệu chứng tiểu đường là gì?" if name == "Nguy cơ cao" else None)
        print("\n" + "=" * 70)
        print(f"{name} | request_id={r['request_id']} | status={r['status']}")
        if r["prediction"]:
            print(f"  Dự đoán: {r['prediction']['label']} (score {r['prediction']['score']})")
        if r["rules"]:
            print(f"  Cờ luật: {[f['id'] for f in r['rules']['flags']]} | cần xem xét: {r['needs_human_review']}")
        if r["evidence"]:
            print(f"  Bằng chứng: {len(r['evidence'])} mục, ví dụ: {r['evidence'][0]['text'][:80]}...")
        if r["errors"]:
            print(f"  Lỗi: {r['errors']}")
        print(f"  Trace: {[(t['agent'], t['status']) for t in r['trace']]}")
        if r.get("report") and name == "Nguy cơ cao":
            print("\n" + r["report"])
finally:
    coord.kg.close()
