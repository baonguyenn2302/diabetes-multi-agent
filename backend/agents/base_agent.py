"""Optional interface for Person A's agents. Person B's agents need not inherit it."""
from abc import ABC, abstractmethod
from typing import Any


class BaseAgent(ABC):
    name: str

    @abstractmethod
    def run(self, task: dict[str, Any]) -> dict[str, Any]:
        """Return a response conforming to schemas.agent_messages."""
