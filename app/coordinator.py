"""Coordinator Agent: điều phối các agent theo đúng 12 bước của tài liệu kiến trúc (mục 5.3).

Luồng:
  1 nhận request → 2 tạo request_id → 3 Data Agent → 4-5 lỗi thì DỪNG và trả validation_error
  → 6 DL Agent → 7 Rule Agent → 8 KG/RAG Agent → 9 gom kết quả → 10 Explanation Agent
  → 11 ghi trace (Monitoring) → 12 trả kết quả có cấu trúc.

Nguyên tắc:
  - Giữ tách biệt prediction / rules / evidence (mục 4.2).
  - Lỗi của một agent KHÔNG làm sập luồng: các phần còn lại vẫn trả về, status = "partial".
  - Coordinator không bao giờ ném exception ra ngoài handle().
"""
import time
import uuid
from typing import Any, Callable, Optional

from app.schemas import AgentMessage

DEFAULT_QUESTION = "tiểu đường nguy cơ phòng ngừa lời khuyên"


class CoordinatorAgent:
    NAME = "CoordinatorAgent"
    VERSION = "coord_v1"

    def __init__(self, data_agent, dl_agent, rule_agent, kg_agent,
                 explainer=None, monitor=None, new_id: Optional[Callable[[], str]] = None):
        self.data, self.dl, self.rule, self.kg = data_agent, dl_agent, rule_agent, kg_agent
        self.explainer = explainer          # Explanation Agent (Giai đoạn 6), có thể None
        self.monitor = monitor              # Monitoring Agent (Giai đoạn 7), có thể None
        self._new_id = new_id or (lambda: f"req_{uuid.uuid4().hex[:8]}")

    # ------------------------------------------------------------ public
    def handle(self, raw: Any, question: Optional[str] = None) -> dict:
        rid = self._new_id()                                     # bước 2
        trace: list[dict] = []
        errors: list[dict] = []
        try:
            res = self._pipeline(rid, raw, question, trace, errors)
        except Exception as e:                                   # lớp chắn cuối, không để sập API
            errors.append({"agent": self.NAME, "error": f"{type(e).__name__}: {e}"})
            res = self._compose(rid, "error")
        res["trace"] = trace
        res["errors"] = errors
        self._audit(rid, trace, res["status"], errors)           # bước 11
        return res

    # ------------------------------------------------------------ pipeline
    def _pipeline(self, rid, raw, question, trace, errors) -> dict:
        data = self._call("data", rid, trace, errors, self.data.run, rid, raw)     # bước 3
        if data.status != "ok":                                                    # bước 4-5
            return self._compose(rid, "validation_error")

        feats = data.payload["features"]
        dl = self._call("dl", rid, trace, errors, self.dl.run, rid, feats)          # bước 6
        prediction = dl.payload if dl.status == "ok" else None                     # không có dự đoán thì luật vẫn chạy

        rule = self._call("rule", rid, trace, errors, self.rule.run, rid, feats, prediction)  # bước 7
        kg = self._call("kg", rid, trace, errors, self.kg.run, rid, question or DEFAULT_QUESTION)  # bước 8

        report, explain_ok = None, True
        if self.explainer is None:
            trace.append({"agent": "explain", "status": "skipped", "ms": 0, "version": None})
        else:
            outputs = {"prediction": dl, "rules": rule, "knowledge": kg}            # bước 9
            exp = self._call("explain", rid, trace, errors, self.explainer.run, rid, outputs)  # bước 10
            explain_ok = exp.status == "ok"
            report = exp.payload.get("report") if explain_ok else None

        core_ok = all(m.status == "ok" for m in (dl, rule, kg)) and explain_ok
        return self._compose(rid, "ok" if core_ok else "partial", dl, rule, kg, report)

    # ------------------------------------------------------------ helpers
    def _call(self, name, rid, trace, errors, fn, *args) -> AgentMessage:
        t0 = time.perf_counter()
        try:
            msg = fn(*args)
            if not isinstance(msg, AgentMessage):
                raise TypeError(f"{name} không trả về AgentMessage")
        except Exception as e:
            msg = AgentMessage.fail(rid, name, f"{type(e).__name__}: {e}")
        trace.append({"agent": name, "status": msg.status,
                      "ms": int((time.perf_counter() - t0) * 1000), "version": msg.version})
        if msg.status != "ok":
            errors.append({"agent": name, "error": msg.error or "không rõ lỗi"})
        return msg

    @staticmethod
    def _compose(rid, status, dl=None, rule=None, kg=None, report=None) -> dict:
        ok = lambda m: m is not None and m.status == "ok"
        rules = rule.payload if ok(rule) else None
        return {
            "request_id": rid,
            "status": status,                                    # ok | partial | validation_error | error
            "prediction": dl.payload if ok(dl) else None,        # đầu ra model
            "rules": rules,                                      # cờ luật
            "evidence": kg.evidence if ok(kg) else [],           # bằng chứng có nguồn
            "report": report,                                    # báo cáo (sau Giai đoạn 6)
            "needs_human_review": bool(rules and rules.get("needs_human_review")),
            "errors": [],
            "trace": [],
        }

    def _audit(self, rid, trace, status, errors):
        if self.monitor is None:
            return
        try:
            self.monitor.record(rid, trace, status)
        except Exception as e:
            errors.append({"agent": "monitor", "error": f"{type(e).__name__}: {e}"})


def build_default_coordinator(explainer=None, monitor=None) -> CoordinatorAgent:
    """Dựng coordinator với agent thật: cần model trong models/ và Neo4j đã nạp KB."""
    from app.agents.data_agent import PatientDataAgent
    from app.agents.dl_agent import DLPredictionAgent
    from app.agents.rule_agent import RuleBasedAgent
    from app.agents.kg_rag_agent import KGRAGAgent
    from app.agents.explanation_agent import ExplanationAgent
    kg = KGRAGAgent.from_settings()
    dl = DLPredictionAgent.from_paths()
    rule = RuleBasedAgent.from_runner(kg.query)
    if explainer is None:
        explainer = ExplanationAgent()
    if monitor is None:
        from app.agents.monitoring_agent import MonitoringAgent
        monitor = MonitoringAgent()
    return CoordinatorAgent(PatientDataAgent(), dl, rule, kg, explainer, monitor)
