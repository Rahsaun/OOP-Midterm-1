"""Interchangeable persistence adapters for the zombie simulation."""
from abc import ABC, abstractmethod
from copy import deepcopy
import json
from pathlib import Path


class StateStorage(ABC):
    """Storage contract used by the simulation controller."""

    @abstractmethod
    def save_state(self, state: dict) -> None:
        """Save a complete, JSON-compatible simulation snapshot."""

    @abstractmethod
    def load_state(self) -> dict | None:
        """Return the latest snapshot or None if none exists."""


class JSONStorage(StateStorage):
    """Persist one snapshot in a local JSON file."""

    def __init__(self, filename: str = "game_state.json"):
        self.filename = Path(filename)

    def save_state(self, state: dict) -> None:
        self.filename.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.filename.with_name(self.filename.name + ".tmp")
        temporary.write_text(json.dumps(state, indent=2), encoding="utf-8")
        temporary.replace(self.filename)

    def load_state(self) -> dict | None:
        if not self.filename.exists():
            return None
        return json.loads(self.filename.read_text(encoding="utf-8"))


class PostgreSQLStorage(StateStorage):
    """Persist a snapshot in PostgreSQL (requires psycopg and a database URL).

    For safety, database credentials are provided at runtime, never hardcoded.
    """

    def __init__(self, connection_string: str):
        if not connection_string:
            raise ValueError("A PostgreSQL connection string is required")
        self.connection_string = connection_string
        self._ensure_table()

    def _connect(self):
        try:
            import psycopg
        except ImportError as exc:
            raise RuntimeError(
                "Install PostgreSQL support using: pip install -r requirements-postgres.txt"
            ) from exc
        return psycopg.connect(self.connection_string)

    def _ensure_table(self):
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """CREATE TABLE IF NOT EXISTS simulation_state (
                        id INTEGER PRIMARY KEY,
                        state JSONB NOT NULL,
                        saved_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                    )"""
                )

    def save_state(self, state: dict) -> None:
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """INSERT INTO simulation_state (id, state, saved_at)
                       VALUES (1, %s::jsonb, NOW())
                       ON CONFLICT (id) DO UPDATE
                       SET state = EXCLUDED.state, saved_at = NOW()""",
                    (json.dumps(state),),
                )

    def load_state(self) -> dict | None:
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT state FROM simulation_state WHERE id = 1")
                row = cursor.fetchone()
        if row is None:
            return None
        value = row[0]
        return json.loads(value) if isinstance(value, str) else deepcopy(value)
