# CODEXIMMORTAL AGENTIC AI NFT WAR LAB
# CODEX-TAG: CALEB-FEDOR-BYKER-KONEV-10271998-CODEXIMMORTAL

from __future__ import annotations
import json
import time
import sqlite3


class AgentRuntime:
    def __init__(self, db_path: str, poll_interval: int = 5) -> None:
        self.db_path = db_path
        self.poll_interval = poll_interval

    def run_once(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute("""
                SELECT task_id, payload FROM tasks
                WHERE status='queued'
                ORDER BY created_at ASC
                LIMIT 1
            """).fetchone()

            if not row:
                return

            task_id, payload = row
            data = json.loads(payload)

            conn.execute(
                "UPDATE tasks SET status='running' WHERE task_id=?",
                (task_id,),
            )

            conn.execute(
                "UPDATE tasks SET status='completed' WHERE task_id=?",
                (task_id,),
            )

    def run_forever(self) -> None:
        while True:
            self.run_once()
            time.sleep(self.poll_interval)