"""Tách file markdown tri thức thành các đoạn để nạp vào ChromaDB."""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Callable

MAX_CHARS = 900
UNTITLED = "Mở đầu"
PART_RE = re.compile(r"^PHẦN\s*(\d+)\b")


@dataclass
class Chunk:
    section: str      # tiêu đề "##"
    subsection: str   # tiêu đề "###", có thể rỗng
    text: str         # nội dung thân đoạn

    @property
    def document(self) -> str:
        """Văn bản đưa vào embedding, kèm tiêu đề để truy vấn chính xác hơn."""
        head = self.section if not self.subsection else f"{self.section} › {self.subsection}"
        return f"{head}\n\n{self.text}"


def part_number(section: str) -> int | None:
    """'PHẦN 10: ...' -> 10. Tiêu đề không phải mục PHẦN thì trả về None."""
    m = PART_RE.match(section)
    return int(m.group(1)) if m else None


def parse_frontmatter(raw: str) -> tuple[dict[str, str], str]:
    """Đọc khối YAML đơn giản ở đầu file (chỉ cặp key: value)."""
    lines = raw.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, raw
    try:
        end = lines.index("---", 1)
    except ValueError:
        return {}, raw
    meta: dict[str, str] = {}
    for line in lines[1:end]:
        m = re.match(r"^([A-Za-z_]+):\s*(.*)$", line)
        if m:
            meta[m.group(1)] = m.group(2).strip().strip('"')
    return meta, "\n".join(lines[end + 1:])


def split_sections(body: str) -> list[tuple[str, str, str]]:
    """Trả về danh sách (section, subsection, text)."""
    result: list[tuple[str, str, str]] = []
    section, subsection = UNTITLED, ""
    buf: list[str] = []

    def flush() -> None:
        text = "\n".join(buf).strip()
        if text:
            result.append((section, subsection, text))
        buf.clear()

    for line in body.splitlines():
        if line.startswith("## "):
            flush()
            section, subsection = line[3:].strip(), ""
        elif line.startswith("### "):
            flush()
            subsection = line[4:].strip()
        else:
            buf.append(line)
    flush()
    return result


def pack(text: str, max_chars: int = MAX_CHARS) -> list[str]:
    """Gộp các đoạn văn liên tiếp sao cho mỗi nhóm không vượt quá max_chars."""
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    out: list[str] = []
    cur = ""
    for p in paragraphs:
        if cur and len(cur) + len(p) + 2 > max_chars:
            out.append(cur)
            cur = p
        else:
            cur = f"{cur}\n\n{p}" if cur else p
    if cur:
        out.append(cur)
    return out


def chunk_markdown(
    body: str,
    keep: Callable[[str, str], bool] | None = None,
) -> list[Chunk]:
    """Tách thân markdown thành đoạn.

    keep(section, subsection) trả True nếu giữ đoạn đó.
    Nếu không truyền, giữ tất cả.
    """
    chunks: list[Chunk] = []
    for section, subsection, text in split_sections(body):
        if keep is not None and not keep(section, subsection):
            continue
        for piece in pack(text):
            chunks.append(Chunk(section, subsection, piece))
    return chunks