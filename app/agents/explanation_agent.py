"""Explanation Agent (template): tạo báo cáo hỗ trợ quyết định từ kết quả các agent.

Không dùng LLM. Mọi nội dung đều sinh từ dữ liệu có cấu trúc (dự đoán, cờ luật, bằng chứng),
nên kết quả tái lập được và mỗi nhận định đều truy được về một cờ luật hoặc một nguồn.

Input : outputs = {"prediction": AgentMessage, "rules": AgentMessage, "knowledge": AgentMessage}
Output: AgentMessage(payload={"report": str, "sections": dict, "warnings": list, ...})
Thiếu phần nào (agent lỗi hoặc chưa chạy) thì báo rõ trong báo cáo, không làm hỏng toàn bộ báo cáo.
"""
from app.schemas import AgentMessage
from app.sources import get_source

LEVEL_ORDER = {"high": 0, "review": 1, "medium": 2, "low": 3}
LEVEL_VN = {"high": "mức cao", "review": "cần xem xét", "medium": "mức trung bình", "low": "mức thấp"}
MAX_EVIDENCE = 10
ADVICE_RELATIONS = ("HELPS_PREVENT", "HELPS_DETECT_EARLY")

DISCLAIMER = ("Đây là hệ thống hỗ trợ học tập và nghiên cứu. Nội dung dưới đây **không phải chẩn đoán xác định** "
              "và không thay thế ý kiến của bác sĩ.")
LIMITS = [
    "Mô hình được huấn luyện trên một dataset công khai, chưa được kiểm chứng lâm sàng.",
    "Dataset không phân biệt tiểu đường loại 1 và loại 2, và không ghi rõ thời điểm đo đường huyết.",
    "Ngưỡng và luật là tham khảo, cần chuyên gia y tế thẩm định trước khi dùng trong thực tế.",
    "Hệ thống không kê đơn thuốc, không đưa ra liều dùng và không thay thế xét nghiệm hay khám bệnh.",
]
GENERAL_ADVICE = [
    "Nên đi khám bác sĩ để được kiểm tra và tư vấn, đặc biệt khi có yếu tố nguy cơ hoặc triệu chứng.",
    "Khám và xét nghiệm đường huyết định kỳ tại cơ sở y tế đạt chuẩn là cách phát hiện sớm tốt nhất.",
]
RECHECK_ADVICE = "Nên làm lại xét nghiệm HbA1c hoặc đường huyết tại cơ sở y tế đạt chuẩn để xác nhận kết quả."
TITLES = [
    ("prediction", "1. Dự đoán của mô hình"),
    ("flags", "2. Cờ luật và yếu tố nguy cơ"),
    ("review", "3. Mâu thuẫn cần chuyên gia xem xét"),
    ("evidence", "4. Bằng chứng từ cơ sở tri thức"),
    ("advice", "5. Gợi ý"),
    ("limits", "6. Giới hạn"),
]


class ExplanationAgent:
    NAME = "ExplanationAgent"
    VERSION = "explain_tpl_v1"

    def run(self, request_id: str, outputs: dict) -> AgentMessage:
        try:
            return self._build(request_id, outputs or {})
        except Exception as e:
            return AgentMessage.fail(request_id, self.NAME, f"{type(e).__name__}: {e}", self.VERSION)

    # ------------------------------------------------------------ dựng báo cáo
    def _build(self, rid, outputs):
        pred = outputs.get("prediction")
        rules = outputs.get("rules")
        kg = outputs.get("knowledge")

        warnings = []
        for label, m in (("Dự đoán", pred), ("Luật", rules), ("Bằng chứng", kg)):
            if m is None:
                warnings.append(f"{label}: không có kết quả")
            elif m.status != "ok":
                warnings.append(f"{label}: {m.error or 'lỗi không rõ'}")

        flags = self._flags(rules)
        review = bool(rules is not None and rules.status == "ok" and rules.payload.get("needs_human_review"))
        evidence = self._evidence(kg)

        sections = {
            "prediction": self._sec_prediction(pred),
            "flags": self._sec_flags(flags, rules),
            "review": self._sec_review(flags, rules),
            "evidence": self._sec_evidence(kg, evidence),
            "advice": self._sec_advice(flags, review, evidence),
            "limits": [f"- {x}" for x in LIMITS],
        }
        report = self._render(rid, sections, warnings)
        return AgentMessage.ok(
            rid, self.NAME,
            payload={"report": report, "sections": sections, "warnings": warnings,
                     "n_flags": len(flags), "n_evidence": len(evidence)},
            version=self.VERSION)

    @staticmethod
    def _render(rid, sections, warnings):
        out = ["## Báo cáo hỗ trợ quyết định (tham khảo)", f"*Mã yêu cầu: {rid}*", "", f"> {DISCLAIMER}", ""]
        for key, title in TITLES:
            out.append(f"### {title}")
            out += sections[key]
            out.append("")
        if warnings:
            out.append("### Lưu ý về dữ liệu đầu ra")
            out += [f"- {w}" for w in warnings]
        return "\n".join(out).rstrip() + "\n"

    # ------------------------------------------------------------ đầu vào
    @staticmethod
    def _flags(rules):
        if rules is None or rules.status != "ok":
            return []
        return list(rules.payload.get("flags", []))

    @staticmethod
    def _evidence(kg):
        """Bằng chứng đã bỏ trùng theo nội dung, giữ thứ tự."""
        if kg is None or kg.status != "ok":
            return []
        seen, out = set(), []
        for e in kg.evidence:
            t = e.get("text")
            if t and t not in seen:
                seen.add(t)
                out.append(e)
        return out

    # ------------------------------------------------------------ từng mục
    @staticmethod
    def _sec_prediction(pred):
        if pred is None or pred.status != "ok":
            why = pred.error if pred is not None and pred.error else "không có kết quả"
            return [f"- Không có kết quả dự đoán ({why})."]
        p = pred.payload
        return [
            f"- **Kết quả:** {p.get('label', '?')} (xác suất {p.get('score', 0):.2f}, ngưỡng {p.get('threshold', 0):g}).",
            "- Đây là dự đoán thống kê của mô hình, không phải chẩn đoán xác định.",
            "- Mô hình chỉ phân biệt có hoặc không có nguy cơ tiểu đường, không phân biệt loại 1 và loại 2.",
        ]

    @staticmethod
    def _sec_flags(flags, rules):
        if rules is None or rules.status != "ok":
            return ["- Không có kết quả luật do lỗi hoặc chưa chạy."]
        main = [f for f in flags if f.get("category") != "conflict"]
        if not main:
            return ["- Không có cờ nào."]
        main.sort(key=lambda f: (LEVEL_ORDER.get(f.get("level"), 9), f.get("id", "")))
        lines = []
        for f in main:
            src = get_source(f.get("source_id"))[0]
            lines.append(f"- **[{f['id']}] {LEVEL_VN.get(f.get('level'), f.get('level'))}:** {f['text']} "
                         f"_Nguồn: {src}_")
        return lines

    @staticmethod
    def _sec_review(flags, rules):
        if rules is None or rules.status != "ok":
            return ["- Không kiểm tra được mâu thuẫn vì không có kết quả luật."]
        conflicts = [f for f in flags if f.get("category") == "conflict"]
        if not conflicts and not rules.payload.get("needs_human_review"):
            return ["- Không phát hiện mâu thuẫn giữa mô hình và các xét nghiệm."]
        lines = ["- ⚠️ **Cần chuyên gia y tế xem xét** trước khi sử dụng kết quả:"]
        lines += [f"  - [{f['id']}] {f['text']}" for f in conflicts] or \
                 ["  - Luật đánh dấu có mâu thuẫn cần xem xét."]
        return lines

    @staticmethod
    def _sec_evidence(kg, evidence):
        if kg is None or kg.status != "ok":
            return ["- Không truy xuất được bằng chứng từ cơ sở tri thức."]
        if not evidence:
            return ["- Không tìm thấy bằng chứng liên quan."]
        lines = []
        for i, e in enumerate(evidence[:MAX_EVIDENCE], 1):
            src = e.get("source_title") or "Không rõ nguồn"
            url = e.get("source_url") or ""
            tail = f"{src} ({url})" if url else src
            lines.append(f"{i}. {e.get('text', '')}")
            lines.append(f"   _Nguồn: {tail}_")
        return lines

    @staticmethod
    def _sec_advice(flags, review, evidence):
        lines = [f"- {a}" for a in GENERAL_ADVICE]
        if review or any(f.get("level") == "high" for f in flags):
            lines.append(f"- {RECHECK_ADVICE}")
        picked = [e["text"] for e in evidence if e.get("relation") in ADVICE_RELATIONS][:5]
        lines += [f"- {t}" for t in picked]
        return lines
