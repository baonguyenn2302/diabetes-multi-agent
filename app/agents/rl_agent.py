"""RL Agent (CHỈ MÔ PHỎNG): tra chính sách học được trong môi trường giả lập.

- Không nằm trên luồng chẩn đoán của Coordinator. Hệ thống không gọi agent này khi trả kết quả cho bệnh nhân.
- Đầu ra luôn đánh dấu simulated=True. Không đưa ra thuốc, liều dùng hay thay đổi điều trị.
"""
import json
import pathlib
from typing import Optional

from app.schemas import AgentMessage
from sim.followup_env import ACTIONS, CONTENTS, INTERVALS, RISK_LABELS, STATES

NOTE = "Kết quả chỉ từ mô phỏng giả lập. Không áp dụng cho bệnh nhân thật."


class FollowUpPolicyAgent:
    NAME = "RLPolicyAgent"
    VERSION = "rl_sim_v1"

    def __init__(self, policy: dict):
        self.policy = {int(k): tuple(v) for k, v in policy.items()}

    @classmethod
    def from_file(cls, path: str):
        data = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
        return cls({int(k): tuple(v["action"]) for k, v in data.items()})

    def run(self, request_id: str, risk_state: int) -> AgentMessage:
        try:
            if risk_state not in STATES:
                return AgentMessage.fail(request_id, self.NAME, f"Trạng thái không hợp lệ: {risk_state}", self.VERSION)
            c, i = self.policy[risk_state]
            if (c, i) not in ACTIONS:
                return AgentMessage.fail(request_id, self.NAME, f"Hành động ngoài danh sách cho phép: {(c, i)}", self.VERSION)
            return AgentMessage.ok(request_id, self.NAME, payload={
                "simulated": True,
                "risk_state": RISK_LABELS[risk_state],
                "content": CONTENTS[c],
                "follow_up_months": INTERVALS[i],
                "note": NOTE,
            }, version=self.VERSION)
        except Exception as e:
            return AgentMessage.fail(request_id, self.NAME, f"{type(e).__name__}: {e}", self.VERSION)
