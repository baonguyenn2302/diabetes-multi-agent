"""Monitoring / Audit Agent: ghi trace của mỗi request và tính thống kê vận hành.

- Ghi vào logs/audit.jsonl, mỗi dòng là một JSON (tài liệu kiến trúc, Layer 6).
- KHÔNG ghi giá trị đặc trưng của bệnh nhân. Chỉ ghi request_id, kết quả, thời gian và
  trạng thái từng bước, phiên bản agent. Việc này hạn chế dữ liệu cá nhân nằm trong log.
- Ghi log không bao giờ làm hỏng request: lỗi ghi file được đếm lại, không ném ra ngoài.
"""
import datetime
import json
import math
import threading
from collections import Counter
from typing import Optional

from app.config import settings, resolve_path


def percentile(values: list, p: float) -> Optional[float]:
    """Phân vị theo phương pháp nearest-rank. Danh sách rỗng trả về None."""
    if not values:
        return None
    s = sorted(values)
    k = math.ceil(p / 100 * len(s))
    return s[max(k, 1) - 1]


class MonitoringAgent:
    NAME = "MonitoringAgent"
    VERSION = "monitor_v1"

    def __init__(self, path: Optional[str] = None):
        self.path = resolve_path(path or settings.audit_log_path)
        self._lock = threading.Lock()
        self.write_errors = 0

    # ------------------------------------------------------------ ghi
    def record(self, request_id: str, trace: list, outcome: str) -> dict:
        trace = list(trace or [])
        rec = {
            "ts": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
            "request_id": request_id,
            "outcome": outcome,
            "total_ms": sum(int(t.get("ms") or 0) for t in trace),
            "steps": [t.get("agent") for t in trace],
            "agent_ms": {t.get("agent"): t.get("ms") for t in trace},
            "agent_status": {t.get("agent"): t.get("status") for t in trace},
            "agents_failed": [t.get("agent") for t in trace if t.get("status") == "error"],
            "versions": {t.get("agent"): t.get("version") for t in trace if t.get("version")},
            "monitor_version": self.VERSION,
            "write_ok": True,
        }
        try:
            line = json.dumps(rec, ensure_ascii=False)
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self._lock:
                with self.path.open("a", encoding="utf-8") as f:
                    f.write(line + "\n")
        except OSError:
            rec["write_ok"] = False
            with self._lock:
                self.write_errors += 1
        return rec

    # ------------------------------------------------------------ đọc & thống kê
    def read_records(self):
        """Trả về (các bản ghi hợp lệ, số dòng không đọc được)."""
        good, bad = [], 0
        if not self.path.exists():
            return good, bad
        with self.path.open(encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    good.append(json.loads(line))
                except json.JSONDecodeError:
                    bad += 1
        return good, bad

    def summary(self, last_n: Optional[int] = None) -> dict:
        recs, bad = self.read_records()
        if last_n:
            recs = recs[-last_n:]

        outcomes = Counter(r.get("outcome") for r in recs)
        totals = [r.get("total_ms", 0) for r in recs if r.get("outcome") != "validation_error"]

        per: dict = {}
        for r in recs:
            status_map = r.get("agent_status") or {}
            for agent, ms in (r.get("agent_ms") or {}).items():
                if status_map.get(agent) == "skipped":
                    continue
                st = per.setdefault(agent, {"calls": 0, "errors": 0, "ms": []})
                st["calls"] += 1
                if status_map.get(agent) == "error":
                    st["errors"] += 1
                if isinstance(ms, (int, float)):
                    st["ms"].append(ms)

        agents = {
            a: {"calls": s["calls"],
                "error_rate": round(s["errors"] / s["calls"], 4),
                "avg_ms": round(sum(s["ms"]) / len(s["ms"]), 1) if s["ms"] else None,
                "p95_ms": percentile(s["ms"], 95)}
            for a, s in per.items()
        }
        return {
            "n_requests": len(recs),
            "invalid_lines": bad,
            "outcomes": dict(outcomes),
            "total_ms": ({"avg": round(sum(totals) / len(totals), 1),
                          "p50": percentile(totals, 50),
                          "p95": percentile(totals, 95)} if totals else None),
            "agents": agents,
        }
