"""Quick database inspector — proves the SQLite store holds/returns data.

Run from the repo root:
    python backend/check_db.py
"""
from __future__ import annotations

import os
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.core.config import get_settings  # noqa: E402


def main() -> None:
    db_path = get_settings().database_url.replace("sqlite:///", "")
    print(f"DB file : {db_path}")
    print(f"exists  : {os.path.exists(db_path)}")
    if not os.path.exists(db_path):
        print("No database yet — run:  python backend/seed.py")
        return
    print(f"size    : {os.path.getsize(db_path)} bytes\n")

    con = sqlite3.connect(db_path)
    cur = con.cursor()

    tables = [
        r[0]
        for r in cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )
    ]
    print("Row counts per table:")
    for t in tables:
        count = cur.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        print(f"  {t:24s} {count}")

    print("\nLatest 5 tickets (stored values):")
    rows = cur.execute(
        "SELECT id, status, category, department, ROUND(confidence, 2) "
        "FROM tickets ORDER BY id DESC LIMIT 5"
    ).fetchall()
    if not rows:
        print("  (none)")
    for r in rows:
        print(f"  #{r[0]:<4} status={r[1]:<12} category={r[2]} dept={r[3]} conf={r[4]}")

    print("\nUsers:")
    for r in cur.execute("SELECT id, email, role_name FROM users ORDER BY id LIMIT 20"):
        print(f"  #{r[0]:<4} {r[1]:<40} {r[2]}")

    con.close()


if __name__ == "__main__":
    main()
