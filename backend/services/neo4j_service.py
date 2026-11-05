"""Dịch vụ Neo4j: kiểm tra kết nối và truy vấn đồ thị.

Nếu chưa cấu hình, chưa cài driver hoặc không kết nối được, các hàm báo trạng thái
unavailable rõ ràng và KHÔNG trả về dữ liệu giả.
"""
from __future__ import annotations

import os
from typing import Any

STATUS_OK = "ok"
STATUS_UNAVAILABLE = "unavailable"


class Neo4jUnavailableError(RuntimeError):
    """Neo4j chưa cấu hình, chưa cài driver, không kết nối được hoặc truy vấn lỗi."""


class Neo4jService:
    def __init__(
        self,
        uri: str | None = None,
        user: str | None = None,
        password: str | None = None,
    ):
        self.uri = uri if uri is not None else os.getenv("NEO4J_URI", "")
        self.user = user if user is not None else os.getenv("NEO4J_USER", "neo4j")
        self.password = password if password is not None else os.getenv("NEO4J_PASSWORD", "")
        self._driver = None

    @property
    def configured(self) -> bool:
        return bool(self.uri)

    def _connect(self):
        if self._driver is not None:
            return self._driver
        if not self.configured:
            raise Neo4jUnavailableError("Chưa cấu hình NEO4J_URI")
        try:
            from neo4j import GraphDatabase
        except ImportError as exc:
            raise Neo4jUnavailableError("Chưa cài thư viện neo4j") from exc
        try:
            driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
            driver.verify_connectivity()
        except Exception as exc:
            raise Neo4jUnavailableError(f"Không kết nối được Neo4j: {exc}") from exc
        self._driver = driver
        return driver

    def health(self) -> dict[str, str]:
        try:
            self._connect()
        except Neo4jUnavailableError as exc:
            return {"status": STATUS_UNAVAILABLE, "detail": str(exc)}
        return {"status": STATUS_OK, "detail": "Đã kết nối Neo4j"}

    def run(self, cypher: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """Chạy truy vấn Cypher. Ném Neo4jUnavailableError nếu không chạy được."""
        driver = self._connect()
        try:
            with driver.session() as session:
                return [record.data() for record in session.run(cypher, params or {})]
        except Exception as exc:
            raise Neo4jUnavailableError(f"Truy vấn Neo4j lỗi: {exc}") from exc

    def close(self) -> None:
        if self._driver is not None:
            self._driver.close()
            self._driver = None