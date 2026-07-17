from __future__ import annotations

from typing import Dict, List, Optional
from uuid import uuid4
from datetime import datetime

from integration.task_models import SubagentInstance, SubagentRole, TaskStatus, SubTask


class SubagentRuntime:
    def __init__(self) -> None:
        self.registry: Dict[str, SubagentInstance] = {}

    def spawn_subagent(self, role: SubagentRole, capabilities: Optional[List[str]] = None) -> SubagentInstance:
        agent = SubagentInstance(
            agent_id=f"agent-{uuid4().hex[:10]}",
            role=role,
            capabilities=capabilities or [],
            status="IDLE",
        )
        self.registry[agent.agent_id] = agent
        return agent

    def assign_subtask(self, agent_id: str, task_id: str, subtask: SubTask) -> SubagentInstance:
        agent = self.registry[agent_id]
        agent.assigned_task_id = task_id
        agent.assigned_subtask_id = subtask.subtask_id
        agent.status = "RUNNING"
        agent.last_heartbeat = datetime.utcnow()
        subtask.status = TaskStatus.RUNNING
        return agent

    def heartbeat(self, agent_id: str, status: str = "RUNNING") -> None:
        agent = self.registry[agent_id]
        agent.status = status
        agent.last_heartbeat = datetime.utcnow()

    def complete_assignment(self, agent_id: str, subtask: SubTask) -> None:
        agent = self.registry[agent_id]
        agent.status = "IDLE"
        agent.assigned_subtask_id = None
        subtask.status = TaskStatus.COMPLETED
        agent.last_heartbeat = datetime.utcnow()

    def retire_subagent(self, agent_id: str) -> None:
        if agent_id in self.registry:
            self.registry[agent_id].status = "RETIRED"

    def list_subagents(self) -> List[SubagentInstance]:
        return list(self.registry.values())