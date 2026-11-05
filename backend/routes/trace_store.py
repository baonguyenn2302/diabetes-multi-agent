"""Transient API execution traces, not a database and not a fake agent state.
SQLite persistence will replace/supplement this in Step 5.
"""
from __future__ import annotations
from collections import deque
from threading import Lock


class RecentTraces:
    def __init__(self, limit=100):
        self._entries = deque(maxlen=limit)
        self._lock = Lock()

    def add(self, response):
        record = {"session_id": response.get("session_id"), "intent": response.get("intent"),
                  "status": response.get("status"), "agent_trace": response.get("agent_trace", [])}
        with self._lock:
            self._entries.append(record)

    def latest(self, session_id=None):
        with self._lock:
            for entry in reversed(self._entries):
                if session_id is None or entry["session_id"] == session_id:
                    return {"session_id": entry["session_id"], "intent": entry["intent"],
                            "status": entry["status"], "agent_trace": list(entry["agent_trace"])}
        return None
