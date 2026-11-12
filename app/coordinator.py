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
    def handle_chat(self, question: str, context: Optional[dict] = None) -> dict:
        """Luồng vấn đáp: chỉ dùng KG/RAG Agent để trả lời câu hỏi về tiểu đường."""
        rid = self._new_id()
        trace: list[dict] = []
        errors: list[dict] = []
        try:
            kg = self._call("kg", rid, trace, errors, self.kg.run, rid, question)
            if kg.status == "ok":
                from app.agents.kg_rag_agent import format_context
                answer = format_context(kg.evidence)
                if context:
                    ctx_note = "Thông tin bệnh nhân đi kèm: " + ", ".join(
                        f"{k}={v}" for k, v in context.items())
                    answer = ctx_note + "\n\n" + answer
                matched = kg.payload.get("matched_entities", [])
                intents = kg.payload.get("intents", [])
                status = "ok"
            else:
                answer = kg.error or "Không thể truy xuất tri thức."
                matched, intents = [], []
                status = "error"
            return {
                "status": status,
                "answer": answer,
                "evidence": kg.evidence if kg.status == "ok" else [],
                "matched_entities": matched,
                "intents": intents,
                "errors": errors,
                "trace": trace,
            }
        except Exception as e:
            errors.append({"agent": self.NAME, "error": f"{type(e).__name__}: {e}"})
            return {
                "status": "error",
                "answer": f"Lỗi hệ thống: {e}",
                "evidence": [],
                "matched_entities": [],
                "intents": [],
                "errors": errors,
                "trace": trace,
            }

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

    def handle_chat(self, question: str, context: Optional[dict[str, Any]] = None,
                    history: Optional[list] = None) -> dict:
        """Xử lý hội thoại/vấn đáp độc lập: chỉ truy vấn KG/RAG, không chạy mô hình DL."""
        rid = f"chat_{uuid.uuid4().hex[:8]}"
        trace: list[dict] = []
        errors: list[dict] = []

        q = (question or "").strip() or DEFAULT_QUESTION
        kg = self._call("kg", rid, trace, errors, self.kg.run, rid, q)

        answer = self._compose_chat_answer(q, kg, context)
        status = "ok" if kg.status == "ok" else "partial"

        res = {
            "request_id": rid,
            "status": status,
            "answer": answer,
            "evidence": kg.evidence if kg.status == "ok" else [],
            "has_patient_context": bool(context),
            "trace": trace,
            "errors": errors,
        }
        self._audit(rid, trace, status, errors)
        return res

    def _compose_chat_answer(self, question: str, kg_msg: AgentMessage,
                             context: Optional[dict[str, Any]]) -> str:
        lines: list[str] = []

        # 1. Ngữ cảnh bệnh nhân (nếu người dùng chủ động liên kết từ trang đánh giá)
        if context:
            ctx_items = []
            if "gender" in context:
                ctx_items.append(f"Giới tính: {context['gender']}")
            if "age" in context:
                ctx_items.append(f"Tuổi: {context['age']}")
            if "bmi" in context:
                ctx_items.append(f"BMI: {context['bmi']}")
            if "HbA1c_level" in context:
                ctx_items.append(f"HbA1c: {context['HbA1c_level']}%")
            if "blood_glucose_level" in context:
                ctx_items.append(f"Đường huyết: {context['blood_glucose_level']} mg/dL")
            if "risk_label" in context:
                ctx_items.append(f"Mức nguy cơ dự đoán: {context['risk_label']}")
            elif "prediction" in context and isinstance(context["prediction"], dict):
                ctx_items.append(f"Mức nguy cơ: {context['prediction'].get('label', '')}")

            if ctx_items:
                lines.append(f"> 📋 **Hồ sơ bệnh nhân ghi nhận:** {', '.join(ctx_items)}.\n")

        # 2. Bằng chứng trích xuất từ Knowledge Graph
        evidence_list = kg_msg.evidence if kg_msg and kg_msg.status == "ok" else []
        if evidence_list:
            seen_texts = set()
            unique_evidence = []
            for e in evidence_list:
                t = e.get("text")
                if t and t not in seen_texts:
                    seen_texts.add(t)
                    unique_evidence.append(e)

            lines.append("Dựa trên cơ sở tri thức y khoa chuẩn về bệnh tiểu đường:")
            for e in unique_evidence[:8]:
                text = e.get("text")
                src_title = e.get("source_title") or "Tài liệu y tế"
                src_url = e.get("source_url")
                if src_url:
                    lines.append(f"- **{text}**  \n  ↳ *Nguồn: [{src_title}]({src_url})*")
                else:
                    lines.append(f"- **{text}**  \n  ↳ *Nguồn: {src_title}*")
        else:
            lines.append(
                "Cơ sở tri thức chưa có thông tin chi tiết trực tiếp cho câu hỏi này. "
                "Theo các khuyến cáo chung về bệnh tiểu đường, việc duy trì chế độ dinh dưỡng lành mạnh, "
                "vận động thể lực hợp lý và kiểm tra đường huyết định kỳ là những yếu tố quan trọng hàng đầu."
            )

        # 3. Khuyến cáo y khoa
        lines.append(
            "\n---\n*Lưu ý: Nội dung trên được truy xuất từ Knowledge Graph (ADA, WHO, Vinmec...) nhằm mục đích hỗ trợ tra cứu học tập. "
            "Thông tin không thay thế cho chẩn đoán hoặc chỉ định điều trị của bác sĩ chuyên khoa.*"
        )
        return "\n".join(lines)


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
