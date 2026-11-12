"""Test API FastAPI bằng TestClient. Tự bỏ qua nếu chưa cài fastapi/httpx."""
import pytest

pytest.importorskip("fastapi")
pytest.importorskip("httpx")

from fastapi import HTTPException                       # noqa: E402
from fastapi.testclient import TestClient               # noqa: E402

from app.api import app, get_coordinator                # noqa: E402
from tests.test_coordinator_integration import LOW, build  # noqa: E402

client = TestClient(app)


def _with(coord_factory):
    app.dependency_overrides[get_coordinator] = coord_factory


def _clear():
    app.dependency_overrides.clear()


def test_health():
    r = client.get("/health")
    assert r.status_code == 200 and r.json()["status"] == "ok"


def test_assess_ok():
    _with(lambda: build(lambda f: 0.1))
    try:
        r = client.post("/assess", json={"features": LOW})
        assert r.status_code == 200 and r.json()["status"] == "ok"
        assert r.json()["prediction"]["label"] == "nguy cơ thấp"
    finally:
        _clear()


def test_assess_validation_error_is_422_with_errors():
    _with(lambda: build(lambda f: 0.1))
    try:
        r = client.post("/assess", json={"features": {"gender": "Female", "age": "abc"}})
        assert r.status_code == 422 and r.json()["status"] == "validation_error"
        assert r.json()["errors"]
    finally:
        _clear()


def test_assess_wrong_body_type_is_422():
    r = client.post("/assess", json={"features": "không phải object"})
    assert r.status_code == 422


def test_unavailable_system_returns_503():
    def down():
        raise HTTPException(status_code=503, detail="không khởi tạo được")
    _with(down)
    try:
        r = client.post("/assess", json={"features": LOW})
        assert r.status_code == 503
    finally:
        _clear()


def test_audit_summary_endpoint_shape():
    r = client.get("/audit/summary")
    assert r.status_code == 200 and "n_requests" in r.json()
