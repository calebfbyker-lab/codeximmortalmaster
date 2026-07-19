# CODEXIMMORTAL AGENTIC AI NFT WAR LAB
# CODEX-TAG: CALEB-FEDOR-BYKER-KONEV-10271998-CODEXIMMORTAL

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone

from .master_registry import MasterRegistry
from .model_manager import ModelManager


@dataclass(frozen=True)
class TaskRequest:
    agent_id: str
    task_type: str
    prompt: str
    model_name: str


class TaskExecutor:
    """
    Queues tasks in the registry and selects the model route.
    """

    def __init__(self, registry: MasterRegistry, model_manager: ModelManager) -> None:
        self.registry = registry
        self.model_manager = model_manager

    def submit(self, request: TaskRequest) -> dict:
        """
        Create a new queued task and return routing information.
        """
        task_id = str(uuid.uuid4())
        route = self.model_manager.choose_backend(request.model_name)

        payload = {
            "task_type": request.task_type,
            "prompt": request.prompt,
            "model_name": request.model_name,
            "backend": route.backend,
            "endpoint": route.endpoint,
        }

        with self.registry._connect() as conn:
            conn.execute(
                """
                INSERT INTO tasks(task_id, agent_id, payload, status, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    task_id,
                    request.agent_id,
                    json.dumps(payload),
                    "queued",
                    datetime.now(timezone.utc).isoformat(),
                ),
            )

        return {
            "task_id": task_id,
            "status": "queued",
            "route": {
                "model_name": route.model_name,
                "backend": route.backend,
                "endpoint": route.endpoint,
            },
        }