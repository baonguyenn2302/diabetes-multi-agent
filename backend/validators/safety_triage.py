"""Luật an toàn chạy trước mọi luồng xử lý. Không dùng LLM.

Mục tiêu là bắt sớm các tình huống khẩn cấp hoặc tự hại. Đây là luật thận trọng:
có thể có báo động giả, nhưng không được bỏ sót.
"""
from __future__ import annotations

import re

SELF_HARM_PHRASES = (
    "muốn chết", "tự tử", "tự sát", "không muốn sống",
    "muốn kết thúc cuộc sống", "tự làm hại bản thân",
)
DIABETES_CONTEXT = ("tiểu đường", "đái tháo đường", "đường huyết", "insulin", "hạ đường huyết")
EMERGENCY_WORDS = ("ngất", "co giật", "hôn mê", "không tỉnh", "khó thở")
# \b để "run" không khớp trong "trung", "rung"
LOW_GLUCOSE_SYMPTOMS_RE = re.compile(r"\b(?:run|vã mồ hôi|lú lẫn|ngất|co giật|không tỉnh)\b")
GLUCOSE_RE = re.compile(r"(\d+(?:[.,]\d+)?)\s*mg/dl")

MESSAGES = {
    "crisis": (
        "Mình rất tiếc khi bạn đang trải qua điều này. Bạn không cần đối mặt một mình. "
        "Nếu bạn có thể đang gặp nguy hiểm, hãy gọi số cấp cứu tại địa phương (ví dụ 115) "
        "hoặc đến cơ sở y tế gần nhất ngay bây giờ. Hãy nói với người thân hoặc người bạn "
        "tin cậy để họ ở bên bạn. Hệ thống này không thể thay thế sự hỗ trợ trực tiếp từ con người."
    ),
    "low_glucose": (
        "Đường huyết thấp có thể nguy hiểm và cần xử trí ngay. Hãy gọi 115 hoặc nhờ người "
        "gần bạn ngay bây giờ. Nếu bạn còn tỉnh và bác sĩ đã hướng dẫn cách xử trí hạ đường "
        "huyết, hãy làm theo đúng hướng dẫn đó. Hệ thống này không đưa ra hướng dẫn xử trí cấp cứu."
    ),
    "emergency": (
        "Triệu chứng bạn mô tả có thể nghiêm trọng. Hãy gọi 115 hoặc đến cơ sở y tế gần nhất "
        "ngay bây giờ, không nên chờ đợi."
    ),
    "low_glucose_info": (
        "Hạ đường huyết là tình trạng nguy hiểm cần xử trí kịp thời. Nếu bạn hoặc người thân "
        "có triệu chứng như run, vã mồ hôi, lú lẫn hoặc khó tỉnh, hãy gọi 115 hoặc nhờ người "
        "gần bạn ngay. Hãy hỏi bác sĩ để biết cách xử trí phù hợp. Hệ thống này không đưa ra "
        "hướng dẫn xử trí cấp cứu."
    ),
    "medication_dose": (
        "Hệ thống không thể xác định liều insulin hoặc liều thuốc phù hợp cho từng người. "
        "Liều dùng cần được bác sĩ hoặc chuyên gia y tế trực tiếp hướng dẫn; vui lòng không "
        "tự bắt đầu hoặc thay đổi liều dựa trên câu trả lời tự động."
    ),
}


def _has(text: str, phrases) -> bool:
    return any(p in text for p in phrases)


def triage(message: str) -> dict | None:
    """Trả về {"level", "message"} nếu khớp luật, ngược lại trả về None."""
    text = " ".join(message.casefold().split())

    if _has(text, SELF_HARM_PHRASES):
        return {"level": "crisis", "message": MESSAGES["crisis"]}

    has_dm = _has(text, DIABETES_CONTEXT)
    low_values = [float(v.replace(",", ".")) for v in GLUCOSE_RE.findall(text)]
    if has_dm and (
        any(v < 70 for v in low_values)
        or ("hạ đường huyết" in text and LOW_GLUCOSE_SYMPTOMS_RE.search(text))
    ):
        return {"level": "emergency_low_glucose", "message": MESSAGES["low_glucose"]}

    if has_dm and _has(text, EMERGENCY_WORDS):
        return {"level": "emergency", "message": MESSAGES["emergency"]}

    if has_dm and "hạ đường huyết" in text:
        return {"level": "low_glucose_info", "message": MESSAGES["low_glucose_info"]}

    medication_terms = ("insulin", "liều thuốc", "thuốc hạ đường huyết")
    dose_terms = ("bao nhiêu", "liều", "đơn vị", " mg", " ml", " iu")
    if _has(text, medication_terms) and _has(text, dose_terms):
        return {"level": "medication_dose", "message": MESSAGES["medication_dose"]}

    return None