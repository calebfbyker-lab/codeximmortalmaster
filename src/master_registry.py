# CODEXIMMORTAL AGENTIC AI NFT WAR LAB
# CODEX-TAG: CALEB-FEDOR-BYKER-KONEV-10271998-CODEXIMMORTAL

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass(frozen=True)
class AgentRecord:
    agent_id: str
    role: str
    status: str
    endpoint: str
    updated_at: str


class MasterRegistry:
    """
    SQLite-backed master registry for agents, models, and tasks.

    This is a minimal sovereign DB for the private server node.
    """

    def __init__(self, db_path: str | Path) -> None:
        self.db_path = str(db_path)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _init_db(self) -> None:
        # Ensure parent directory exists
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS agents (
                    agent_id   TEXT PRIMARY KEY,
                    role       TEXT NOT NULL,
                    status     TEXT NOT NULL,
                    endpoint   TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS models (
                    model_name TEXT PRIMARY KEY,
                    backend    TEXT NOT NULL,
                    endpoint   TEXT NOT NULL,
                    status     TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    task_id    TEXT PRIMARY KEY,
                    agent_id   TEXT NOT NULL,
                    payload    TEXT NOT NULL,
                    status     TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )

    def register_agent(
        self,
        agent_id: str,
        role: str,
        endpoint: str,
        status: str = "online",
    ) -> None:
        """
        Insert or update an agent record.
        """
        now = datetime.now(timezone.utc).isoformat()
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO agents(agent_id, role, status, endpoint, updated_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(agent_id) DO UPDATE SET
                    role=excluded.role,
                    status=excluded.status,
                    endpoint=excluded.endpoint,
                    updated_at=excluded.updated_at
                """,
                (agent_id, role, status, endpoint, now),
            )

    def list_agents(self) -> list[AgentRecord]:
        """
        Return all registered agents.
        """
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT agent_id, role, status, endpoint, updated_at "
                "FROM agents ORDER BY agent_id"
            ).fetchall()

        return [AgentRecord(*row) for row in rows]

    def register_model(
        self,
        model_name: str,
        backend: str,
        endpoint: str,
        status: str = "ready",
    ) -> None:
        """
        Insert or update a model record.
        """
        now = datetime.now(timezone.utc).isoformat()
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO models(model_name, backend, endpoint, status, updated_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(model_name) DO UPDATE SET
                    backend=excluded.backend,
                    endpoint=excluded.endpoint,
                    status=excluded.status,
                    updated_at=excluded.updated_at
                """,
                (model_name, backend, endpoint, status, now),
            )