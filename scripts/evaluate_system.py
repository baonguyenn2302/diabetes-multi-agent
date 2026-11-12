"""Đánh giá toàn hệ thống. Chạy trên máy có model đã huấn luyện và Neo4j đã nạp KB:

    python scripts/evaluate_system.py              # bench 30 ca
    python scripts/evaluate_system.py --bench 100  # đo độ trễ kỹ hơn

Ghi reports/evaluation.md và reports/evaluation.json. Mất vài phút vì mỗi ca bench gọi Neo4j.
"""
import argparse
import datetime
import json
import pathlib
import random
import sys
import tempfile

import joblib
import numpy as np
from sklearn.metrics import roc_auc_score

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scripts.train_model import load_and_clean, split_data          # noqa: E402
from app.config import settings, resolve_path                         # noqa: E402
from app.features import FEATURE_NAMES, CATEGORICAL_FEATURES          # noqa: E402
from app.evaluation import (ablation, kg_coverage, latency_summary, metrics,   # noqa: E402
                            render_markdown, rule_alert, same_metrics, select_cases)

KG_QUESTIONS = [
    "Triệu chứng của tiểu đường là gì?",
    "Chỉ số HbA1c bao nhiêu thì bị tiền tiểu đường?",
    "Ngưỡng HbA1c để chẩn đoán tiểu đường",
    "Những ai dễ bị tiểu đường type 2?",
    "Tiền tiểu đường là gì và có nguy hiểm không?",
    "Biến chứng của tiểu đường nguy hiểm không?",
    "Tôi nên ăn uống và vận động thế nào để phòng bệnh?",
    "Xét nghiệm đường huyết lúc đói bao nhiêu thì cao?",
    "Người cao tuổi cần lưu ý gì về biến chứng tiểu đường?",
    "Tiểu đường thai kỳ có ảnh hưởng gì không?",
]


def to_payload(row):
    out = {}
    for f in FEATURE_NAMES:
        v = row[f]
        out[f] = str(v) if f in CATEGORICAL_FEATURES else (int(v) if f in ("hypertension", "heart_disease") else float(v))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bench", type=int, default=30, help="số ca đo độ trễ qua toàn bộ Coordinator")
    ap.add_argument("--cases", type=int, default=5, help="số ca mỗi nhóm TP/FN/FP/TN trong bảng ca thử")
    a = ap.parse_args()

    # 1. Tập test giống hệt lúc huấn luyện (cùng seed, cùng cách chia)
    df, info = load_and_clean(resolve_path("data/diabetes_prediction_dataset.csv"))
    _, _, X_te, _, _, y_te = split_data(df)

    # 2. Model DL: chạy batch
    from tensorflow import keras
    model = keras.models.load_model(resolve_path(settings.model_path))
    pre = joblib.load(resolve_path(settings.preprocessor_path))
    meta = json.loads(resolve_path(settings.meta_path).read_text(encoding="utf-8"))
    thr = float(meta["threshold"])
    scores = np.asarray(model.predict(np.asarray(pre.transform(X_te), dtype="float32"), verbose=0)).ravel()
    y = y_te.values.astype(int)
    dl = (scores >= thr).astype(int)
    model_m = metrics(y, dl)
    model_m["roc_auc"] = round(float(roc_auc_score(y, scores)), 4)
    check = same_metrics(model_m, meta["metrics_test"])

    # 3. Lớp Rule trên toàn bộ tập test (ngưỡng đọc từ KG)
    from app.agents.kg_rag_agent import KGRAGAgent
    from app.agents.rule_agent import RuleBasedAgent
    kg = KGRAGAgent.from_settings()
    recs = X_te.to_dict("records")
    abl, alerts, rule_error = None, None, None
    try:
        rule = RuleBasedAgent.from_runner(kg.query)
        alerts, reviews = [], []
        for i, row in enumerate(recs):
            m = rule.run("eval", to_payload(row), {"prediction": int(dl[i])})
            if m.status != "ok":
                raise RuntimeError(m.error)
            alerts.append(rule_alert(m.payload["flags"]))
            reviews.append(bool(m.payload["needs_human_review"]))
        abl = ablation(y, dl, alerts, reviews)
    except Exception as e:
        rule_error = f"{type(e).__name__}: {e}"

    rows = [{"idx": i, "y": int(y[i]), "dl": int(dl[i]), "score": round(float(scores[i]), 4),
             "alert": alerts[i] if alerts else None} for i in range(len(y))]
    cases = select_cases(rows, k=a.cases)

    # 4. Bench qua toàn bộ Coordinator: đo độ trễ và kiểm tra nhất quán với batch
    from app.coordinator import build_default_coordinator
    from app.agents.monitoring_agent import MonitoringAgent
    from collections import Counter
    coord = build_default_coordinator(monitor=MonitoringAgent(pathlib.Path(tempfile.mkdtemp()) / "bench.jsonl"))
    idxs = random.Random(42).sample(range(len(y)), min(a.bench, len(y)))
    traces, statuses, match = [], Counter(), 0
    try:
        for i in idxs:
            res = coord.handle(to_payload(recs[i]))
            statuses[res["status"]] += 1
            traces.append(res["trace"])
            if res["prediction"] and res["prediction"]["prediction"] == int(dl[i]):
                match += 1
    finally:
        coord.kg.close()

    # 5. Độ phủ nguồn của KG
    kg_rows = []
    try:
        for q in KG_QUESTIONS:
            r = kg.run("eval", q, top_k=8)
            kg_rows.append({"question": q, "evidence": r.evidence if r.status == "ok" else []})
    finally:
        kg.close()

    data = {
        "generated_at": datetime.datetime.now().isoformat(timespec="seconds"),
        "model": {"metrics": model_m, "card": meta["metrics_test"], "matches_card": check,
                  "n_test": int(len(y)), "threshold": thr, "version": meta.get("model_version")},
        "dataset": info,
        "ablation": abl, "rule_error": rule_error,
        "cases": cases,
        "latency": latency_summary(traces),
        "consistency": {"match": match, "n": len(idxs), "statuses": dict(statuses)},
        "kg": kg_coverage(kg_rows),
    }
    out = ROOT / "reports"
    out.mkdir(exist_ok=True)
    (out / "evaluation.json").write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    (out / "evaluation.md").write_text(render_markdown(data), encoding="utf-8")
    print(f"Đã ghi {out/'evaluation.md'}")
    print(f"Khớp model card: {check} | ablation: {'có' if abl else 'không (' + str(rule_error) + ')'}")
    print(f"Nhất quán Coordinator/batch: {match}/{len(idxs)} | trạng thái: {dict(statuses)}")


if __name__ == "__main__":
    main()
