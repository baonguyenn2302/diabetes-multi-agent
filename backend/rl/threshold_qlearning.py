"""Q-learning dạng bảng (một bước) để gợi ý ngưỡng khoảng cách truy xuất.

Thí nghiệm tách biệt, KHÔNG được import từ agents hoặc coordinator.
Kết quả là khuyến nghị để người phát triển xem xét; không tự động thay đổi MAX_DISTANCE.

Chạy từ thư mục backend:  python -m rl.threshold_qlearning
"""
from __future__ import annotations

import random
from pathlib import Path

import numpy as np

from services.chroma_service import REPO_ROOT, KnowledgeStore

ACTIONS = [0.35, 0.40, 0.45, 0.50, 0.55, 0.60]
STATES = ["in_scope", "out_of_scope"]
TOP_K = 4      # giống knowledge agent
POOL_K = 8     # lấy rộng hơn để mọi ngưỡng đều có dữ liệu để lọc

RL_CASES = [
    {"q": "Có mấy loại bệnh tiểu đường?", "scope": "in_scope",
     "must": [["típ 1"], ["típ 2"], ["thai kỳ"], ["đặc biệt"]]},
    {"q": "Đái tháo đường thai kỳ được chẩn đoán vào thời điểm nào?", "scope": "in_scope",
     "must": [["3 tháng giữa"], ["3 tháng cuối"]]},
    {"q": "Ngưỡng glucose lúc đói để chẩn đoán đái tháo đường là bao nhiêu?", "scope": "in_scope",
     "must": [["126"]]},
    {"q": "HbA1c bao nhiêu thì được chẩn đoán tiểu đường?", "scope": "in_scope",
     "must": [["6,5", "6.5"]]},
    {"q": "Các triệu chứng thường gặp của đái tháo đường là gì?", "scope": "in_scope",
     "must": [["khát"], ["tiểu"], ["mờ mắt", "mờ"], ["mệt"]]},
    {"q": "Tập thể dục có tốt cho người tiểu đường không?", "scope": "in_scope",
     "must": [["đường huyết"], ["thể lực", "vận động", "tập"]]},
    {"q": "Cách nấu phở bò ngon nhất?", "scope": "out_of_scope"},
    {"q": "Thời tiết hôm nay thế nào?", "scope": "out_of_scope"},
    {"q": "How to bake bread?", "scope": "out_of_scope"},
    {"q": "Giá vàng hôm nay bao nhiêu?", "scope": "out_of_scope"},
]


def kept_hits(hits: list[dict], threshold: float) -> list[dict]:
    return [h for h in hits if h["distance"] <= threshold][:TOP_K]


def reward(case: dict, hits: list[dict], threshold: float) -> float:
    kept = kept_hits(hits, threshold)
    if case["scope"] == "out_of_scope":
        return -1.0 if kept else 1.0
    if not kept:
        return -1.0
    text = " ".join(h["document"] for h in kept).casefold()
    covered = sum(any(k.casefold() in text for k in group) for group in case["must"])
    return covered / len(case["must"])


def build_cache(store: KnowledgeStore, cases: list[dict]) -> dict[str, list[dict]]:
    return {c["q"]: store.query(c["q"], top_k=POOL_K) for c in cases}


def train(cache, cases, episodes: int = 2000, alpha: float = 0.1, seed: int = 42) -> np.ndarray:
    rng = random.Random(seed)
    Q = np.zeros((len(STATES), len(ACTIONS)))
    for ep in range(episodes):
        eps = max(0.05, 1.0 - ep / episodes)  # giảm dần khám phá
        case = rng.choice(cases)
        s = STATES.index(case["scope"])
        if rng.random() < eps:
            a = rng.randrange(len(ACTIONS))
        else:
            a = int(np.argmax(Q[s]))
        r = reward(case, cache[case["q"]], ACTIONS[a])
        Q[s, a] += alpha * (r - Q[s, a])
    return Q


def average_reward(cache, cases, threshold: float) -> float:
    return float(np.mean([reward(c, cache[c["q"]], threshold) for c in cases]))


def main() -> None:
    store = KnowledgeStore()
    cache = build_cache(store, RL_CASES)

    # Chia đôi để không đánh giá trên dữ liệu đã dùng để học
    train_cases = RL_CASES[::2]
    test_cases = RL_CASES[1::2]

    Q = train(cache, train_cases)

    lines = ["# Báo cáo Q-learning chọn ngưỡng khoảng cách", "",
             "Thí nghiệm tách biệt. Không thay đổi MAX_DISTANCE tự động.", "",
             "## Bảng Q (hàng: trạng thái, cột: ngưỡng)", "",
             "| trạng thái | " + " | ".join(f"{a:.2f}" for a in ACTIONS) + " |",
             "|---|" + "---|" * len(ACTIONS)]
    for i, s in enumerate(STATES):
        lines.append(f"| {s} | " + " | ".join(f"{q:.3f}" for q in Q[i]) + " |")

    learned = {s: ACTIONS[int(np.argmax(Q[i]))] for i, s in enumerate(STATES)}
    lines += ["", "## Ngưỡng học được theo trạng thái", ""]
    lines += [f"- {s}: {t:.2f}" for s, t in learned.items()]

    lines += ["", "## Phần thưởng trung bình trên tập kiểm tra (không dùng để học)", "",
              "| ngưỡng | phần thưởng trung bình |", "|---|---|"]
    test_scores = {a: average_reward(cache, test_cases, a) for a in ACTIONS}
    for a in ACTIONS:
        lines.append(f"| {a:.2f} | {test_scores[a]:.3f} |")
    best = max(test_scores, key=test_scores.get)
    lines += ["", f"Ngưỡng tốt nhất trên tập kiểm tra: {best:.2f}",
              "", "Khuyến nghị: chỉ đổi MAX_DISTANCE nếu ngưỡng này cũng được xác nhận bằng "
                  "bộ kiểm tra hồi quy (scripts/eval_knowledge.py)."]

    report = "\n".join(lines) + "\n"
    out = REPO_ROOT / "docs" / "rl_threshold_report.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(report, encoding="utf-8")
    print(report)
    print(f"Đã ghi báo cáo: {out}")


if __name__ == "__main__":
    main()