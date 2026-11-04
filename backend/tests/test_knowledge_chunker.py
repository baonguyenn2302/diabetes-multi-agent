from services.knowledge_chunker import chunk_markdown, parse_frontmatter, part_number

SAMPLE = """---
source_title: "Tài liệu thử"
publisher: "Cơ quan thử"
---

Lời dẫn mở đầu.

## PHẦN 1: ĐỊNH NGHĨA

Đoạn một.

Đoạn hai.

### 1. Chẩn đoán

Nội dung chẩn đoán.

## CHỈ ĐẠO BIÊN SOẠN

Không liên quan.
"""


def test_frontmatter_parsed():
    meta, body = parse_frontmatter(SAMPLE)
    assert meta["source_title"] == "Tài liệu thử"
    assert meta["publisher"] == "Cơ quan thử"
    assert body.lstrip().startswith("Lời dẫn")


def test_sections_and_subsections():
    _, body = parse_frontmatter(SAMPLE)
    labels = [(c.section, c.subsection) for c in chunk_markdown(body)]
    assert ("Mở đầu", "") in labels
    assert ("PHẦN 1: ĐỊNH NGHĨA", "") in labels
    assert ("PHẦN 1: ĐỊNH NGHĨA", "1. Chẩn đoán") in labels


def test_document_contains_heading_context():
    _, body = parse_frontmatter(SAMPLE)
    chunk = next(c for c in chunk_markdown(body) if c.subsection == "1. Chẩn đoán")
    assert chunk.document.startswith("PHẦN 1: ĐỊNH NGHĨA › 1. Chẩn đoán")


def test_long_section_is_split():
    long_text = "\n\n".join(["Câu dài " * 40] * 10)
    chunks = chunk_markdown(f"## PHẦN 2\n\n{long_text}")
    assert len(chunks) > 1
    assert all(len(c.text) <= 900 for c in chunks)


def test_part_number_exact():
    assert part_number("PHẦN 1: ĐỊNH NGHĨA") == 1
    assert part_number("PHẦN 10: KHUYẾN CÁO") == 10
    assert part_number("PHẦN 7 : CHẨN ĐOÁN") == 7
    assert part_number("CHỈ ĐẠO BIÊN SOẠN") is None


def test_filter_keeps_only_matching_part():
    _, body = parse_frontmatter(SAMPLE)
    chunks = chunk_markdown(body, lambda s, sub: part_number(s) == 1)
    assert chunks
    assert all(part_number(c.section) == 1 for c in chunks)


def test_filter_by_subsection():
    _, body = parse_frontmatter(SAMPLE)
    chunks = chunk_markdown(body, lambda s, sub: sub.startswith("1."))
    assert chunks
    assert all(c.subsection.startswith("1.") for c in chunks)


def test_filter_does_not_match_prefix():
    body = "## PHẦN 1: A\n\nNội dung một.\n\n## PHẦN 10: B\n\nNội dung mười."
    chunks = chunk_markdown(body, lambda s, sub: part_number(s) in {1})
    assert [c.section for c in chunks] == ["PHẦN 1: A"]