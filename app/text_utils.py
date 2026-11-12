"""Chuẩn hóa văn bản tiếng Việt để so khớp (bỏ dấu, hạ chữ thường)."""
import re
import unicodedata


def normalize_text(s: str) -> str:
    """'Tiền tiểu đường!' -> 'tien tieu duong'; 'HbA1c_level' -> 'hba1c level'."""
    s = s.replace("đ", "d").replace("Đ", "D")
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = re.sub(r"[^a-z0-9]+", " ", s.lower())
    return s.strip()
