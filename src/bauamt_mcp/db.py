from __future__ import annotations

import os
import sqlite3
from pathlib import Path


DEFAULT_DATABASE_PATH = "data/bauamt_permits.db"


def get_database_path() -> Path:
    return Path(os.getenv("DATABASE_PATH", DEFAULT_DATABASE_PATH))


def get_connection() -> sqlite3.Connection:
    db_path = get_database_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database() -> None:
    schema_path = Path("sql/schema.sql")

    if not schema_path.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_path}")

    with get_connection() as conn:
        conn.executescript(schema_path.read_text(encoding="utf-8"))
        conn.commit()