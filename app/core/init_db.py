"""
Creates the SQLite audit log database (Chapter 6.12: Audit Logger).
Run with: python -m app.core.init_db
"""

import sqlite3
from pathlib import Path

DB_PATH = Path("data/logs/promptshield.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    user_id TEXT,
    prompt TEXT NOT NULL,
    risk_score INTEGER NOT NULL,
    attack_category TEXT NOT NULL,
    action_taken TEXT NOT NULL,
    detection_evidence TEXT
);
"""


def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute(SCHEMA)
    conn.commit()
    conn.close()
    print(f"Initialized audit database at {DB_PATH}")


if __name__ == "__main__":
    init_db()
