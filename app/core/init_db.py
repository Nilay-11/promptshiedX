"""
Creates the SQLite audit log database (Chapter 6.12: Audit Logger).
Run with: python -m app.core.init_db
"""

import os
import sqlite3
from pathlib import Path

if os.environ.get("VERCEL") == "1":
    DB_PATH = Path("/tmp/promptshield.db")
else:
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


def log_audit(user_id: str | None, prompt: str, risk_score: int, attack_category: str, action_taken: str, detection_evidence: str | None = None):
    """
    Inserts a row into the audit_log table. Creates database and tables if they do not exist.
    """
    import datetime
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    try:
        # Ensure table is initialized
        conn.execute(SCHEMA)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO audit_log (timestamp, user_id, prompt, risk_score, attack_category, action_taken, detection_evidence)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                datetime.datetime.utcnow().isoformat() + "Z",  # Store as UTC ISO string with Z indicator
                user_id,
                prompt,
                risk_score,
                attack_category,
                action_taken,
                detection_evidence
            )
        )
        conn.commit()
    finally:
        conn.close()


if __name__ == "__main__":
    init_db()

