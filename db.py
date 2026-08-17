"""طبقة SQLite بسيطة وآمنة لذاكرة المستخدم."""

import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime


class Database:
    def __init__(self, path: str):
        self.path = path
        directory = os.path.dirname(path)
        if directory:
            os.makedirs(directory, exist_ok=True)
        self._init_schema()

    @contextmanager
    def connection(self):
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def _init_schema(self):
        with self.connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    kind TEXT NOT NULL CHECK(kind IN ('note', 'task')),
                    content TEXT NOT NULL,
                    completed INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL
                )
            """)

    def add(self, user_id: int, kind: str, content: str) -> int:
        with self.connection() as conn:
            cur = conn.execute(
                "INSERT INTO memories(user_id, kind, content, created_at) VALUES (?, ?, ?, ?)",
                (user_id, kind, content.strip(), datetime.utcnow().isoformat()),
            )
            return int(cur.lastrowid)

    def list_items(self, user_id: int, kind: str | None = None, pending_only: bool = False):
        query = "SELECT * FROM memories WHERE user_id = ?"
        params: list[object] = [user_id]
        if kind:
            query += " AND kind = ?"
            params.append(kind)
        if pending_only:
            query += " AND completed = 0"
        query += " ORDER BY id DESC"
        with self.connection() as conn:
            return conn.execute(query, params).fetchall()

    def complete_task(self, user_id: int, task_id: int) -> bool:
        with self.connection() as conn:
            cur = conn.execute(
                "UPDATE memories SET completed = 1 WHERE id = ? AND user_id = ? AND kind = 'task'",
                (task_id, user_id),
            )
            return cur.rowcount > 0

    def delete_item(self, user_id: int, item_id: int) -> bool:
        with self.connection() as conn:
            cur = conn.execute("DELETE FROM memories WHERE id = ? AND user_id = ?", (item_id, user_id))
            return cur.rowcount > 0
