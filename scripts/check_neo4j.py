"""Kiểm tra kết nối Neo4j và nội dung KB.  python scripts/check_neo4j.py"""
import sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from app.config import settings

from neo4j import GraphDatabase
print(f"URI: {settings.neo4j_uri} | user: {settings.neo4j_user} | database: {settings.neo4j_database}")
try:
    with GraphDatabase.driver(settings.neo4j_uri, auth=(settings.neo4j_user, settings.neo4j_password)) as d:
        d.verify_connectivity()
        print("[OK] Kết nối Neo4j")
        rows, _, _ = d.execute_query("MATCH (n:Entity) RETURN count(n) AS n", database_=settings.neo4j_database)
        n = rows[0]["n"]
        print(f"[{'OK' if n > 0 else 'FAIL'}] Số thực thể trong KB: {n}" + ("" if n else "  -> chạy: python scripts/load_kb.py"))
        rows, _, _ = d.execute_query(
            "MATCH (a:Entity)-[r:RISK_FACTOR_FOR]->(:Entity {id:'type2'}) RETURN a.name AS name LIMIT 3",
            database_=settings.neo4j_database)
        print("[INFO] Mẫu yếu tố nguy cơ type 2:", [r["name"] for r in rows])
except Exception as e:
    print(f"[FAIL] {type(e).__name__}: {e}")
    sys.exit(1)
