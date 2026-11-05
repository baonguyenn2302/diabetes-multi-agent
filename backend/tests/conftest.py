import pytest


@pytest.fixture(autouse=True)
def isolate_neo4j_env(monkeypatch):
    """Test đơn vị không được kết nối Neo4j thật, kể cả khi NEO4J_URI được export trong shell.

    Test nào cần Neo4j tự đặt biến bằng monkeypatch.setenv.
    """
    monkeypatch.delenv("NEO4J_URI", raising=False)