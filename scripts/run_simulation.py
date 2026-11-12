"""Huấn luyện và so sánh chính sách trong mô phỏng.   python scripts/run_simulation.py
Ghi reports/rl_simulation.md và reports/rl_policy.json. CHỈ MÔ PHỎNG, không dùng cho bệnh nhân thật."""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from sim.followup_env import CONTENTS, INTERVALS, RISK_LABELS            # noqa: E402
from sim.rl_train import compare, greedy_policy, train                  # noqa: E402

Q = train(episodes=5000, seed=42)
res = compare(Q, episodes=500)
policy = greedy_policy(Q)

out = ROOT / "reports"
out.mkdir(exist_ok=True)
(out / "rl_policy.json").write_text(json.dumps(
    {str(s): {"action": list(a), "content": CONTENTS[a[0]], "follow_up_months": INTERVALS[a[1]]}
     for s, a in policy.items()}, indent=2, ensure_ascii=False), encoding="utf-8")

L = ["# Mô phỏng chính sách theo dõi (RL, chỉ mô phỏng)", "",
     "> Môi trường giả lập. Xác suất chuyển trạng thái là giả định, không phải số liệu lâm sàng. "
     "Không áp dụng cho bệnh nhân thật.", "",
     "## Chính sách học được", "",
     "| Mức nguy cơ giả lập | Nội dung | Tái khám sau (tháng) |", "|---|---|---|"]
for s, a in policy.items():
    L.append(f"| {RISK_LABELS[s]} | {CONTENTS[a[0]]} | {INTERVALS[a[1]]} |")
L += ["", "## So sánh chính sách (500 episode, cùng chuỗi ngẫu nhiên)", "",
      "| Chính sách | Lợi ích trung bình (có chiết khấu) | Tỉ lệ bước ở nguy cơ cao | Nguy cơ cuối trung bình |",
      "|---|---|---|---|"]
names = {"random": "Ngẫu nhiên", "fixed_6_months_no_content": "Cố định: 6 tháng, không nội dung",
         "simple_rule": "Quy tắc đơn giản", "learned_q_learning": "Học được (Q-learning)"}
for k, v in res.items():
    L.append(f"| {names[k]} | {v['mean_return']} | {v['share_high_risk_steps']} | {v['mean_final_risk']} |")
L += ["", "Lợi ích cao hơn là tốt hơn. Chính sách học được chỉ có ý nghĩa trong môi trường giả lập này."]
(out / "rl_simulation.md").write_text("\n".join(L) + "\n", encoding="utf-8")
print("\n".join(L))
