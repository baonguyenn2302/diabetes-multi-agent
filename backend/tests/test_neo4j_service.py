import pytest

from services.neo4j_service import (
    STATUS_UNAVAILABLE,
    Neo4jService,
    Neo4jUnavailableError,
)


def test_unconfigured_health_is_unavailable():
    svc = Neo4jService(uri="")
    out = svc.health()
    assert out["status"] == STATUS_UNAVAILABLE
    assert "NEO4J_URI" in out["detail"]


def test_unconfigured_run_raises_instead_of_returning_data():
    svc = Neo4jService(uri="")
    with pytest.raises(Neo4jUnavailableError):
        svc.run("MATCH (n) RETURN n LIMIT 1")


def test_unreachable_server_is_unavailable():
    # Cổng 1 không có dịch vụ nào, kết nối sẽ thất bại nhanh
    svc = Neo4jService(uri="bolt://127.0.0.1:1", user="x", password="y")
    out = svc.health()
    assert out["status"] == STATUS_UNAVAILABLE


def test_run_on_unreachable_server_raises():
    svc = Neo4jService(uri="bolt://127.0.0.1:1", user="x", password="y")
    with pytest.raises(Neo4jUnavailableError):
        svc.run("RETURN 1")


def test_env_variable_is_read(monkeypatch):
    monkeypatch.setenv("NEO4J_URI", "bolt://example.invalid:7687")
    svc = Neo4jService()
    assert svc.configured is True


def test_empty_env_is_not_configured(monkeypatch):
    monkeypatch.delenv("NEO4J_URI", raising=False)
    svc = Neo4jService()
    assert svc.configured is False