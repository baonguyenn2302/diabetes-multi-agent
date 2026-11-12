"""Nạp kb/DB_diabet.cypher vào Neo4j (Aura hoặc local).

    python scripts/load_kb.py            # nạp (MERGE nên chạy lại nhiều lần vẫn an toàn)
    python scripts/load_kb.py --reset    # XÓA SẠCH toàn bộ dữ liệu trong database rồi nạp lại
"""
import argparse, sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from app.config import settings, resolve_path
from app.kb_utils import parse_statements


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", default=settings.kb_file)
    ap.add_argument("--reset", action="store_true", help="xóa toàn bộ dữ liệu trước khi nạp")
    a = ap.parse_args()

    path = resolve_path(a.file)
    if not path.exists():
        sys.exit(f"Không thấy file {path}. Chạy trước: python scripts/build_kb.py")
    stmts = parse_statements(path.read_text(encoding="utf-8"))
    schema = [s for s in stmts if s.upper().startswith(("CREATE CONSTRAINT", "CREATE INDEX"))]
    data = [s for s in stmts if s not in schema]
    print(f"Đọc {len(stmts)} câu lệnh ({len(schema)} schema + {len(data)} dữ liệu) từ {path.name}")

    from neo4j import GraphDatabase
    from neo4j.exceptions import AuthError, ServiceUnavailable
    db = settings.neo4j_database
    try:
        with GraphDatabase.driver(settings.neo4j_uri,
                                  auth=(settings.neo4j_user, settings.neo4j_password)) as driver:
            driver.verify_connectivity()
            print(f"Kết nối OK: {settings.neo4j_uri} (database '{db}')")

            if a.reset:
                if input("Sẽ XÓA TOÀN BỘ dữ liệu trong database này. Gõ 'yes' để tiếp tục: ").strip() != "yes":
                    sys.exit("Đã hủy.")
                driver.execute_query("MATCH (n) DETACH DELETE n", database_=db)
                print("Đã xóa dữ liệu cũ.")

            for s in schema:                       # schema chạy riêng, không chung transaction với dữ liệu
                driver.execute_query(s, database_=db)

            def work(tx):
                for s in data:
                    tx.run(s).consume()
            with driver.session(database=db) as session:
                session.execute_write(work)

            rows, _, _ = driver.execute_query(
                "MATCH (n:Entity) RETURN n.kind AS kind, count(*) AS n ORDER BY kind", database_=db)
            print("\nThực thể theo loại:")
            for r in rows:
                print(f"  {r['kind']:<12} {r['n']}")
            for label, cy in [("Nguồn (Source)", "MATCH (s:Source) RETURN count(s) AS n"),
                              ("Quan hệ", "MATCH (:Entity)-[r]->(:Entity) RETURN count(r) AS n")]:
                rows, _, _ = driver.execute_query(cy, database_=db)
                print(f"  {label:<12} {rows[0]['n']}")
            print("\nNạp KB thành công ✅")
    except AuthError:
        sys.exit("Sai tài khoản/mật khẩu Neo4j. Kiểm tra NEO4J_USERNAME / NEO4J_PASSWORD trong .env")
    except ServiceUnavailable as e:
        sys.exit(f"Không kết nối được Neo4j ({e}). Kiểm tra NEO4J_URI, mạng, và instance Aura đã 'Running' chưa.")


if __name__ == "__main__":
    main()
