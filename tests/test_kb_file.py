"""Kiểm tra file kb/DB_diabet.cypher (không cần Neo4j)."""
import pathlib, re, sys
from app.kb_utils import parse_statements
from app.text_utils import normalize_text

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import build_kb

FILE = ROOT / "kb" / "DB_diabet.cypher"


def _stmts():
    assert FILE.exists(), "Thiếu kb/DB_diabet.cypher – chạy: python scripts/build_kb.py"
    return parse_statements(FILE.read_text(encoding="utf-8"))


def test_statement_count_matches_data():
    expected = 2 + len(build_kb.SOURCES) + len(build_kb.NODES) + len(build_kb.RELS)
    assert len(_stmts()) == expected


def test_only_allowed_statement_types():
    for s in _stmts():
        assert s.startswith(("CREATE CONSTRAINT", "MERGE", "MATCH")), s[:60]
        assert s.count("'") % 2 == 0 or "\\'" in s, f"Dấu nháy mất cân bằng: {s[:60]}"


def test_file_is_up_to_date_with_build_script():
    assert FILE.read_text(encoding="utf-8") == build_kb.generate(), \
        "File .cypher cũ so với build_kb.py – chạy lại: python scripts/build_kb.py"


def test_every_fact_has_a_source():
    sources = {s[0] for s in build_kb.SOURCES}
    assert all(n[6] in sources for n in build_kb.NODES)
    assert all(r[3] in sources for r in build_kb.RELS)


def test_diagnostic_thresholds_present():
    """Ngưỡng chẩn đoán chính (Rule Agent ở giai đoạn sau sẽ dùng)."""
    rel = {(a, t): p for a, t, b, s, p in build_kb.RELS if b == "diabetes" and t == "DIAGNOSES"}
    assert rel[("test_hba1c", "DIAGNOSES")]["min_value"] == 6.5
    assert rel[("test_fpg", "DIAGNOSES")]["min_value"] == 126.0
    assert rel[("test_ogtt", "DIAGNOSES")]["min_value"] == 200.0


def test_normalize_text():
    assert normalize_text("Tiền tiểu đường!") == "tien tieu duong"
    assert normalize_text("HbA1c_level") == "hba1c level"
    assert normalize_text("ĐÁI THÁO ĐƯỜNG") == "dai thao duong"
