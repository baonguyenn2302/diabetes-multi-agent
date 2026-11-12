"""Tiện ích đọc file .cypher: tách thành các câu lệnh (mỗi câu kết thúc bằng ';' ở cuối dòng)."""


def parse_statements(text: str) -> list[str]:
    stmts, buf = [], []
    for line in text.splitlines():
        s = line.strip()
        if not buf and (not s or s.startswith("//")):
            continue                      # bỏ dòng trống / chú thích giữa các câu lệnh
        buf.append(line)
        if s.endswith(";"):
            stmts.append("\n".join(buf).strip().rstrip(";").strip())
            buf = []
    if buf:
        raise ValueError("Câu lệnh cuối cùng chưa kết thúc bằng dấu ';'")
    return stmts
