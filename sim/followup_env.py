"""Môi trường MÔ PHỎNG theo dõi bệnh nhân giả lập. KHÔNG dùng cho bệnh nhân thật.

Mục đích: minh họa cách một agent học chính sách chọn nội dung giáo dục và khoảng thời gian tái khám
trong mô phỏng (tài liệu kiến trúc, mục 8). Mọi xác suất chuyển trạng thái là GIẢ ĐỊNH ĐỂ MÔ PHỎNG,
không phải số liệu lâm sàng.

State  : mức nguy cơ giả lập 0 (thấp), 1 (trung bình), 2 (cao)
Action : (nội dung giáo dục, khoảng tái khám). Không có hành động kê thuốc hay thay đổi điều trị.
Reward : trừ theo mức nguy cơ, trừ chi phí nội dung và chi phí liên hệ thường xuyên,
         trừ thêm khi nguy cơ cao mà để cách 6 tháng.
"""
import random

RISK_LABELS = {0: "thấp", 1: "trung bình", 2: "cao"}
CONTENTS = {0: "không có nội dung", 1: "nội dung lối sống", 2: "nội dung dinh dưỡng"}
INTERVALS = {0: 1, 1: 3, 2: 6}                      # tháng giữa hai lần tái khám
ACTIONS = [(c, i) for c in CONTENTS for i in INTERVALS]
STATES = (0, 1, 2)
COST_CONTENT = {0: 0.0, 1: 0.2, 2: 0.2}
COST_INTERVAL = {0: 0.3, 1: 0.1, 2: 0.0}            # liên hệ càng thường xuyên càng tốn kém
HORIZON = 12                                        # số chu kỳ theo dõi mỗi episode
GAMMA = 0.9


def transition_probs(risk: int, content: int, interval: int):
    """Xác suất giả lập: nội dung giáo dục giúp giảm nguy cơ, khoảng cách dài làm tăng nguy cơ."""
    up = (0.15 if content > 0 else 0.05) * {0: 1.3, 1: 1.0, 2: 0.6}[interval]
    down = (0.04 if content > 0 else 0.10) * {0: 0.5, 1: 1.0, 2: 2.0}[interval]
    return min(up, 0.95), min(down, 0.95)


class FollowUpEnv:
    def __init__(self, seed: int = 0, horizon: int = HORIZON):
        self.rng = random.Random(seed)
        self.horizon = horizon
        self.risk = 0
        self.t = 0

    def reset(self, risk: int = None) -> int:
        self.t = 0
        self.risk = risk if risk is not None else self.rng.choice(STATES)
        return self.risk

    def step(self, action):
        if action not in ACTIONS:
            raise ValueError(f"Hành động không hợp lệ: {action}")
        c, i = action
        up, down = transition_probs(self.risk, c, i)
        u = self.rng.random()                        # luôn tiêu một số ngẫu nhiên, để so sánh chính sách công bằng
        if self.risk > 0 and u < up:
            self.risk -= 1
        elif self.risk < 2 and up <= u < up + down:
            self.risk += 1
        self.t += 1
        reward = (-self.risk - COST_CONTENT[c] - COST_INTERVAL[i]
                  - (1.0 if self.risk == 2 and i == 2 else 0.0))
        return self.risk, reward, self.t >= self.horizon
