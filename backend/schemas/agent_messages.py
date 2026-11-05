"""Shared task/result contract, compatible with Person B's agents."""
from uuid import uuid4

STATUSES = frozenset({"pending", "running", "success", "needs_input", "insufficient_evidence", "invalid_input", "error"})
AGENT_NAMES = frozenset({"risk_assessment_agent", "medical_knowledge_agent", "medical_advisor_agent"})


def make_task(session_id, agent_name, action, payload):
    if agent_name not in AGENT_NAMES:
        raise ValueError(f"Unknown agent: {agent_name}")
    if not isinstance(payload, dict):
        raise TypeError("task input must be a dictionary")
    return {"session_id": session_id, "task_id": str(uuid4()), "from": "coordinator", "to": agent_name,
            "task": action, "input": payload, "status": "pending"}


def validate_result(response, task):
    if not isinstance(response, dict):
        raise ValueError("Agent result must be a dictionary")
    for field in ("session_id", "task_id", "agent", "status", "result", "error"):
        if field not in response:
            raise ValueError(f"Agent result missing: {field}")
    if response["session_id"] != task["session_id"] or response["task_id"] != task["task_id"]:
        raise ValueError("Agent result has wrong session_id/task_id")
    if response["agent"] != task["to"] or response["status"] not in STATUSES:
        raise ValueError("Agent result has invalid agent/status")
    if response["result"] is not None and not isinstance(response["result"], dict):
        raise ValueError("Agent result.result must be an object or null")
    return response
