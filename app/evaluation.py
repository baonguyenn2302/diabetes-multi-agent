"""Các hàm đánh giá thuần: không phụ thuộc TensorFlow hay Neo4j nên kiểm thử được mọi nơi.

Gồm: chỉ số phân loại, so sánh ba cấu hình (DL / DL + Rule), chọn ca thử có nhãn,
thống kê độ trễ từ trace, thống kê nguồn của bằng chứng KG, và dựng báo cáo Markdown.
"""
import random
from typing import Optional

from app.agents.monitoring_agent import percentile

# Cờ xét nghiệm mức cao: HbA1c ≥ 6,5% (R01) hoặc đường huyết ≥ 200 mg/dL (R03).
# Đây là lớp "an toàn" của Rule Agent: bắt các ca model bỏ sót nhưng xét nghiệm đã vượt ngưỡng.
ALERT_IDS = ("R01", "R03")

GROUPS = [
    ("TP", "Đúng: model phát hiện được"),
    ("FN", "Bỏ sót: model dự đoán thấp nhưng bệnh nhân có bệnh"),
    ("FP", "Báo động nhầm: model dự đoán cao nhưng không có bệnh"),
    ("TN", "Đúng: model dự đoán thấp và không có bệnh"),
]


def metrics(y_true, y_pred) -> dict:
    tp = fp = tn = fn = 0
    for t, p in zip(y_true, y_pred):
        t, p = int(t), int(p)
        if t == 1 and p == 1:
            tp += 1
        elif t == 0 and p == 1:
            fp += 1
        elif t == 0 and p == 0:
            tn += 1
        else:
            fn += 1
    n = tp + fp + tn + fn
    prec = tp / (tp + fp) if tp + fp else 0.0
    rec = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
    return {"tp": tp, "fp": fp, "tn": tn, "fn": fn,
            "accuracy": round((tp + tn) / n, 4) if n else 0.0,
            "precision": round(prec, 4), "recall": round(rec, 4), "f1": round(f1, 4)}


def rule_alert(flags: list) -> bool:
    """Ca có cờ xét nghiệm mức cao (R01 hoặc R03) thì coi là cảnh báo từ lớp luật."""
    return any(f.get("id") in ALERT_IDS for f in flags)


def ablation(y_true, dl_pred, alert, review=None) -> dict:
    """So sánh DL một mình với DL + Rule. Quyết định của DL + Rule = model dương HOẶC luật cảnh báo."""
    dl_m = metrics(y_true, dl_pred)
    combined = [int(d or a) for d, a in zip(dl_pred, alert)]
    both = metrics(y_true, combined)
    rescued = sum(1 for t, d, a in zip(y_true, dl_pred, alert) if int(t) == 1 and int(d) == 0 and a)
    extra = sum(1 for t, d, a in zip(y_true, dl_pred, alert) if int(t) == 0 and int(d) == 0 and a)
    out = {"dl_only": dl_m, "dl_plus_rule": both,
           "rescued_positives": rescued, "extra_alerts_on_negatives": extra,
           "delta_recall": round(both["recall"] - dl_m["recall"], 4)}
    if review is not None:
        out["review_flags"] = sum(1 for r in review if r)
    return out


def select_cases(rows: list, k: int = 5, seed: int = 42) -> dict:
    """Chọn ngẫu nhiên có seed k ca mỗi nhóm TP/FN/FP/TN, để bảng ca thử lặp lại được."""
    rng = random.Random(seed)
    buckets = {g: [] for g, _ in GROUPS}
    for r in sorted(rows, key=lambda r: r["idx"]):
        buckets[group_of(r["y"], r["dl"])].append(r)
    return {g: rng.sample(v, min(k, len(v))) for g, v in buckets.items()}


def group_of(y: int, p: int) -> str:
    if y == 1:
        return "TP" if p == 1 else "FN"
    return "FP" if p == 1 else "TN"


def latency_summary(trace_lists: list) -> dict:
    """Thống kê thời gian từ trace của nhiều request. Bước 'skipped' không tính."""
    if not trace_lists:
        return {"n": 0, "total": None, "agents": {}}
    per, totals = {}, []
    for tr in trace_lists:
        total = 0
        for t in tr:
            if t.get("status") == "skipped":
                continue
            ms = int(t.get("ms") or 0)
            per.setdefault(t["agent"], []).append(ms)
            total += ms
        totals.append(total)
    return {
        "n": len(trace_lists),
        "total": {"avg": round(sum(totals) / len(totals), 1),
                  "p50": percentile(totals, 50), "p95": percentile(totals, 95)},
        "agents": {a: {"avg": round(sum(v) / len(v), 1), "p95": percentile(v, 95)} for a, v in per.items()},
    }


def kg_coverage(rows: list) -> dict:
    """rows: [{question, evidence: [...]}]. Đếm bằng chứng có nguồn (có URL hoặc tiêu đề thật)."""
    items, total, sourced = [], 0, 0
    for r in rows:
        ev = r.get("evidence") or []
        s = sum(1 for e in ev if e.get("source_url") or
                (e.get("source_title") and e.get("source_title") != "Không rõ nguồn"))
        items.append({"question": r["question"], "n": len(ev), "sourced": s})
        total += len(ev)
        sourced += s
    return {"items": items, "total": total, "sourced": sourced,
            "share": round(sourced / total, 4) if total else None}


def same_metrics(computed: dict, reference: dict, keys=("accuracy", "precision", "recall", "f1", "roc_auc"),
                 tol: float = 0.001) -> bool:
    """Kiểm tra số tính lại có khớp với số đã ghi trong model card (sai số làm tròn)."""
    return all(k in reference and k in computed and abs(computed[k] - reference[k]) <= tol for k in keys)


def render_markdown(d: dict) -> str:
    L = ["# Đánh giá hệ thống hỗ trợ quyết định tiểu đường", "",
         "> Prototype học tập. Số liệu dưới đây phục vụ đánh giá kỹ thuật, không phải bằng chứng lâm sàng.", ""]

    m = d["model"]
    L += ["## 1. Mô hình DL trên tập test", "",
          f"Số ca test: {m['n_test']} · ngưỡng quyết định: {m['threshold']}", "",
          "| Metric | Tính lại | Ghi trong model card | Khớp |", "|---|---|---|---|"]
    for k in ("accuracy", "precision", "recall", "f1", "roc_auc"):
        ok = "✓" if k in m["card"] and abs(m["metrics"].get(k, 9) - m["card"][k]) <= 0.001 else "✗"
        L.append(f"| {k} | {m['metrics'].get(k)} | {m['card'].get(k)} | {ok} |")
    L.append("")

    L += ["## 2. So sánh cấu hình (ablation)", ""]
    a = d.get("ablation")
    if a is None:
        L += [f"Không chạy được lớp Rule: {d.get('rule_error', 'không rõ')}", ""]
    else:
        L += ["| Cấu hình | TP | FP | FN | Precision | Recall | F1 |", "|---|---|---|---|---|---|---|"]
        for name, key in (("DL một mình", "dl_only"), ("DL + Rule", "dl_plus_rule")):
            r = a[key]
            L.append(f"| {name} | {r['tp']} | {r['fp']} | {r['fn']} | {r['precision']} | {r['recall']} | {r['f1']} |")
        L += ["",
              f"- Số ca dương tính mà DL bỏ sót nhưng lớp Rule cảnh báo (được cứu): **{a['rescued_positives']}**.",
              f"- Số báo động thêm trên ca không có bệnh: **{a['extra_alerts_on_negatives']}**.",
              f"- Độ tăng recall: **+{a['delta_recall']}**.",
              f"- Số ca có cờ cần chuyên gia xem xét (mâu thuẫn model và luật): **{a.get('review_flags', 0)}**.", ""]

    L += ["## 3. Ca thử có nhãn (lấy ngẫu nhiên từ tập test, cố định seed)", ""]
    for g, label in GROUPS:
        rows = d["cases"].get(g, [])
        L += [f"**{g}: {label}** ({len(rows)} ca)", ""]
        if rows:
            L += ["| Ca (chỉ số trong test) | Nhãn thật | Score DL | Dự đoán | Cảnh báo luật |", "|---|---|---|---|---|"]
            for r in rows:
                alert = "có" if r.get("alert") else ("không" if r.get("alert") is not None else "–")
                L.append(f"| {r['idx']} | {r['y']} | {r['score']} | {r['dl']} | {alert} |")
        L.append("")

    L += ["## 4. Độ trễ", ""]
    lat = d["latency"]
    if lat["total"]:
        t = lat["total"]
        L += [f"Số request đo: {lat['n']} · tổng thời gian trung bình {t['avg']} ms, p50 {t['p50']} ms, p95 {t['p95']} ms.", "",
              "| Agent | Trung bình (ms) | p95 (ms) |", "|---|---|---|"]
        for ag, v in lat["agents"].items():
            L.append(f"| {ag} | {v['avg']} | {v['p95']} |")
        L.append("")
    L += [f"Kiểm tra nhất quán: {d['consistency']['match']}/{d['consistency']['n']} ca cho cùng dự đoán "
          "khi đi qua toàn bộ Coordinator và khi chạy batch trực tiếp.", ""]
    if d["consistency"].get("statuses"):
        st = d["consistency"]["statuses"]
        L += ["Trạng thái các request đo: " + ", ".join(f"{k}: {v}" for k, v in sorted(st.items())), ""]

    L += ["## 5. Độ phủ nguồn của bằng chứng KG", "",
          "| Câu hỏi | Số bằng chứng | Có nguồn |", "|---|---|---|"]
    kc = d["kg"]
    for it in kc["items"]:
        L.append(f"| {it['question']} | {it['n']} | {it['sourced']} |")
    share = f"{kc['share'] * 100:.0f}%" if kc["share"] is not None else "–"
    L += ["", f"Tổng: {kc['sourced']}/{kc['total']} bằng chứng có nguồn ({share}).", ""]

    L += ["## 6. Hạn chế cần nêu trong báo cáo", "",
          "- Dataset là dữ liệu công khai, không có nhãn loại 1 và loại 2, và không ghi thời điểm đo đường huyết.",
          "- Lớp Rule chỉ bắt các ca có xét nghiệm vượt ngưỡng. Nó không thay thế model và không đo được ca model dự đoán sai theo hướng khác.",
          "- Lớp KG không thay đổi dự đoán. Vai trò của nó là gắn bằng chứng có nguồn cho báo cáo.",
          "- Ngưỡng tuổi 45 và BMI 30 chưa có trong KG. Tri thức chưa được chuyên gia thẩm định.",
          "- Thời gian đo phụ thuộc đường truyền tới Neo4j Aura và máy chạy thử, nên chỉ so sánh tương đối.", ""]
    return "\n".join(L)
