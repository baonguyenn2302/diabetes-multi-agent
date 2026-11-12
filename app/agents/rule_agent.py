"""Rule-Based Agent: áp dụng luật tường minh, sinh cờ có mã và nguồn, phát hiện mâu thuẫn với model.

- Ngưỡng xét nghiệm được ĐỌC TỪ Knowledge Graph (quan hệ DIAGNOSES / INDICATES), không hard-code.
- Cut-off tuổi 45 và BMI 30 là ngưỡng thông dụng, KHÔNG có trong KG nên khai báo riêng tại đây.
- Agent không đưa ra thuốc, liều dùng hay chẩn đoán xác định; mọi cờ đều là gợi ý để kiểm tra thêm.
"""
from app.schemas import AgentMessage

THRESHOLD_QUERY = """
MATCH (t:Entity)-[r:DIAGNOSES|INDICATES]->(d:Entity)
RETURN t.id AS test_id, type(r) AS relation, d.id AS target_id,
       r.min_value AS min_value, r.max_value AS max_value,
       r.criterion AS criterion, r.source_id AS source_id
"""

AGE_CUTOFF = 45            # không có trong KG; xem ghi chú ở đầu file
BMI_CUTOFF = 30.0          # không có trong KG; xem ghi chú ở đầu file
SRC_AGE = "src_longchau_mech"       # KG: rf_age45
SRC_BMI = "src_who"                 # KG: rf_overweight
SRC_HT = "src_vnexpress"            # KG: rf_hypertension
SRC_HD = "src_vnexpress"            # KG: rf_cvd
SRC_SMOKE = "src_who_afro"          # KG: adv_no_tobacco


def thresholds_from_rows(rows: list[dict]) -> dict:
    """Gom các dòng truy vấn KG thành {test_id: {diagnosis_min, prediabetes_min, ...}}."""
    th: dict = {}
    for r in rows:
        t = th.setdefault(r["test_id"], {})
        if r["relation"] == "DIAGNOSES":
            t["diagnosis_min"] = r.get("min_value")
            t["diagnosis_source"] = r.get("source_id")
        elif r["relation"] == "INDICATES":
            t["prediabetes_min"] = r.get("min_value")
            t["prediabetes_max"] = r.get("max_value")
            t["prediabetes_source"] = r.get("source_id")
    return th


REQUIRED = [("test_hba1c", "diagnosis_min"), ("test_hba1c", "prediabetes_min"),
            ("test_fpg", "diagnosis_min"), ("test_fpg", "prediabetes_min"),
            ("test_fpg", "prediabetes_max"), ("test_rpg", "diagnosis_min")]


class RuleBasedAgent:
    NAME = "RuleBasedAgent"
    VERSION = "rules_v1"

    def __init__(self, thresholds: dict):
        self.th = thresholds

    @classmethod
    def from_runner(cls, runner):
        """runner(cypher, params) -> list[dict]; dùng KGRAGAgent.query hoặc bản giả trong test."""
        return cls(thresholds_from_rows(runner(THRESHOLD_QUERY, {})))

    def run(self, request_id: str, features: dict, prediction: dict | None = None) -> AgentMessage:
        try:
            missing = [f"{t}.{k}" for t, k in REQUIRED if self.th.get(t, {}).get(k) is None]
            if missing:
                return AgentMessage.fail(request_id, self.NAME,
                                         f"Thiếu ngưỡng trong KG: {missing}. Chạy lại scripts/load_kb.py",
                                         self.VERSION)
            return self._evaluate(request_id, features, prediction)
        except Exception as e:
            return AgentMessage.fail(request_id, self.NAME, f"{type(e).__name__}: {e}", self.VERSION)

    def _evaluate(self, request_id, features, prediction):
        th_a1c, th_fpg, th_rpg = self.th["test_hba1c"], self.th["test_fpg"], self.th["test_rpg"]
        flags: list[dict] = []

        def add(fid, level, category, text, source):
            flags.append({"id": fid, "level": level, "category": category,
                          "text": text, "source_id": source})

        a1c = features.get("HbA1c_level")
        glu = features.get("blood_glucose_level")
        age, bmi = features.get("age"), features.get("bmi")
        ht, hd = features.get("hypertension"), features.get("heart_disease")
        smoke = features.get("smoking_history")

        # --- Xét nghiệm HbA1c
        if a1c is not None:
            if a1c >= th_a1c["diagnosis_min"]:
                add("R01", "high", "lab",
                    f"HbA1c {a1c:g}% ≥ {th_a1c['diagnosis_min']:g}%: vượt ngưỡng chẩn đoán đái tháo "
                    "đường theo ADA. Cần xét nghiệm lặp lại để xác nhận.",
                    th_a1c["diagnosis_source"])
            elif a1c >= th_a1c["prediabetes_min"]:
                add("R02", "medium", "lab",
                    f"HbA1c {a1c:g}% nằm trong khoảng {th_a1c['prediabetes_min']:g}–"
                    f"{th_a1c['diagnosis_min']:g}%: gợi ý tiền tiểu đường.",
                    th_a1c["prediabetes_source"])

        # --- Đường huyết (dataset không ghi rõ đo lúc đói hay ngẫu nhiên nên gắn cờ có ghi chú)
        if glu is not None:
            if glu >= th_rpg["diagnosis_min"]:
                add("R03", "high", "lab",
                    f"Đường huyết {glu:g} mg/dL ≥ {th_rpg['diagnosis_min']:g}: vượt ngưỡng chẩn đoán. "
                    "Dataset không ghi thời điểm đo nên cần xét nghiệm xác nhận.",
                    th_rpg["diagnosis_source"])
            elif glu >= th_fpg["diagnosis_min"]:
                add("R04", "medium", "lab",
                    f"Đường huyết {glu:g} mg/dL ≥ {th_fpg['diagnosis_min']:g}: vượt ngưỡng lúc đói nếu "
                    "mẫu được đo lúc đói. Dataset không ghi thời điểm đo, cần làm rõ.",
                    th_fpg["diagnosis_source"])
            elif glu >= th_fpg["prediabetes_min"]:
                add("R05", "low", "lab",
                    f"Đường huyết {glu:g} mg/dL nằm trong khoảng {th_fpg['prediabetes_min']:g}–"
                    f"{th_fpg['prediabetes_max']:g}: gợi ý tiền tiểu đường nếu đo lúc đói.",
                    th_fpg["prediabetes_source"])

        # --- Yếu tố nguy cơ
        if age is not None and age >= AGE_CUTOFF:
            add("R06", "low", "risk", f"Tuổi {age:g} ≥ {AGE_CUTOFF}: thuộc nhóm nguy cơ tiểu đường type 2 cao hơn.", SRC_AGE)
        if bmi is not None and bmi >= BMI_CUTOFF:
            add("R07", "medium", "risk", f"BMI {bmi:g} ≥ {BMI_CUTOFF:g}: thừa cân/béo phì là yếu tố nguy cơ.", SRC_BMI)
        if ht == 1:
            add("R08", "low", "risk", "Có tăng huyết áp: là yếu tố nguy cơ của tiểu đường type 2 và biến chứng tim mạch.", SRC_HT)
        if hd == 1:
            add("R09", "medium", "risk", "Có bệnh tim mạch: làm tăng nguy cơ biến chứng tim mạch của tiểu đường.", SRC_HD)
        if smoke in ("current", "former", "ever"):
            add("R10", "low", "advice", "Có tiền sử hút thuốc: nên ngừng hút thuốc lá để giảm nguy cơ biến chứng.", SRC_SMOKE)

        # --- Mâu thuẫn giữa model và luật (theo tài liệu: cần người xem xét)
        conflicts = []
        if prediction is not None:
            p = prediction.get("prediction")
            high_lab = ((a1c is not None and a1c >= th_a1c["diagnosis_min"]) or
                        (glu is not None and glu >= th_rpg["diagnosis_min"]))
            normal_lab = (a1c is not None and glu is not None and
                          a1c < th_a1c["prediabetes_min"] and glu < th_fpg["prediabetes_min"])
            if p == 0 and high_lab:
                add("C01", "review", "conflict",
                    "Model dự đoán nguy cơ thấp nhưng xét nghiệm vượt ngưỡng chẩn đoán. Cần chuyên gia xem xét.",
                    th_a1c["diagnosis_source"])
                conflicts.append("C01")
            if p == 1 and normal_lab:
                add("C02", "review", "conflict",
                    "Model dự đoán nguy cơ cao nhưng HbA1c và đường huyết đều trong ngưỡng bình thường. "
                    "Cần chuyên gia xem xét.", th_a1c["prediabetes_source"])
                conflicts.append("C02")

        return AgentMessage.ok(
            request_id, self.NAME,
            payload={"flags": flags,
                     "needs_human_review": any(f["level"] == "review" for f in flags),
                     "conflicts": conflicts,
                     "n_flags": len(flags)},
            version=self.VERSION)
