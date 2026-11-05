"""Durable execution history for the local demo (stdlib sqlite3, no ORM).

Store chat text and actual Coordinator response/trace. Intentionally do NOT store
health_data: the demo does not need to retain potentially sensitive input values.
"""
from __future__ import annotations

import json
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path


class SQLiteService:
    def __init__(self, db_path):
        self.db_path = str(Path(db_path).resolve())
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self):
        con = sqlite3.connect(self.db_path, timeout=10)
        con.row_factory = sqlite3.Row
        con.execute("PRAGMA foreign_keys = ON")
        con.execute("PRAGMA busy_timeout = 10000")
        return con

    def _initialize(self):
        with closing(self._connect()) as con, con:
            con.executescript("""
                CREATE TABLE IF NOT EXISTS chat_executions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    user_message TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    intent TEXT,
                    status TEXT,
                    response_json TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_chat_session
                    ON chat_executions(session_id, id DESC);
                CREATE TABLE IF NOT EXISTS agent_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    execution_id INTEGER NOT NULL REFERENCES chat_executions(id) ON DELETE CASCADE,
                    position INTEGER NOT NULL,
                    agent TEXT,
                    status TEXT,
                    message TEXT,
                    task_id TEXT
                );
                CREATE INDEX IF NOT EXISTS idx_events_execution
                    ON agent_events(execution_id, position);
            """)

    def add(self, response, message=""):
        """Persist one REAL Coordinator result; returns database execution ID."""
        if not isinstance(response, dict) or not isinstance(response.get("agent_trace"), list):
            raise ValueError("Invalid coordinator response")
        sid = response.get("session_id")
        if not isinstance(sid, str) or not sid:
            raise ValueError("Missing session_id")
        raw = json.dumps(response, ensure_ascii=False, default=str)
        created = datetime.now(timezone.utc).isoformat(timespec="seconds")
        with closing(self._connect()) as con, con:
            cur = con.execute("""INSERT INTO chat_executions
                (session_id, created_at, user_message, answer, intent, status, response_json)
                VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (sid, created, message, response.get("answer", ""),
                 response.get("intent"), response.get("status"), raw))
            execution_id = cur.lastrowid
            con.executemany("""INSERT INTO agent_events
                (execution_id, position, agent, status, message, task_id)
                VALUES (?, ?, ?, ?, ?, ?)""", [
                (execution_id, index, event.get("agent"), event.get("status"),
                 event.get("message"), event.get("task_id"))
                for index, event in enumerate(response["agent_trace"])
                if isinstance(event, dict)
            ])
        return execution_id

    @staticmethod
    def _summary(row):
        response = json.loads(row["response_json"])
        return {"session_id": row["session_id"], "intent": row["intent"],
                "status": row["status"], "agent_trace": response.get("agent_trace", [])}

    def latest(self, session_id=None):
        with closing(self._connect()) as con, con:
            if session_id is None:
                row = con.execute("SELECT * FROM chat_executions ORDER BY id DESC LIMIT 1").fetchone()
            else:
                row = con.execute("SELECT * FROM chat_executions WHERE session_id=? ORDER BY id DESC LIMIT 1", (session_id,)).fetchone()
        return self._summary(row) if row else None

    def history(self, session_id, limit=20):
        if not isinstance(session_id, str) or not session_id:
            raise ValueError("session_id is required")
        if type(limit) is not int or not 1 <= limit <= 100:
            raise ValueError("limit must be between 1 and 100")
        with closing(self._connect()) as con, con:
            rows = con.execute("""SELECT * FROM chat_executions
                WHERE session_id=? ORDER BY id DESC LIMIT ?""", (session_id, limit)).fetchall()
        items = []
        for row in rows:
            response = json.loads(row["response_json"])
            items.append({"execution_id": row["id"], "created_at": row["created_at"],
                          "session_id": row["session_id"], "message": row["user_message"],
                          "answer": row["answer"], "intent": row["intent"],
                          "status": row["status"], "agent_trace": response.get("agent_trace", []),
                          "sources": response.get("sources", []),
                          "warnings": response.get("warnings", []),
                          **({"missing_fields": response["missing_fields"]} if "missing_fields" in response else {})})
        return items

    def health(self):
        try:
            with closing(self._connect()) as con, con:
                con.execute("SELECT 1").fetchone()
            return {"status": "ok", "detail": "SQLite đã kết nối"}
        except sqlite3.Error:
            return {"status": "unavailable", "detail": "Không thể kết nối SQLite"}
