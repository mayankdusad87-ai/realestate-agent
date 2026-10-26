"""
Phase 1: persistent fact memory (SQLite).

Accumulates VERIFIED competitor facts across runs so each report can be grounded
in prior verified data, and stores authoritative TEAM CORRECTIONS that override
web/model output. The backend is a local SQLite file and the public interface is
deliberately small, so it can later be pointed at a durable/shared database
(Postgres, Supabase, etc.) without touching the callers.

Note: on an ephemeral host (e.g. Streamlit Community Cloud) the SQLite file is
reset on every redeploy/restart, so memory persists only within a running
instance. Point MEMORY_DB_PATH at durable storage for cross-deploy persistence.
"""
import sqlite3
import time
from contextlib import closing
from pathlib import Path

# Import the configured DB path, but never let a missing/stale config constant
# take the whole app down - fall back to a local file beside this module.
try:
    from config import MEMORY_DB_PATH
except ImportError:
    MEMORY_DB_PATH = str(Path(__file__).parent / "re_memory.db")

try:
    from config import MAX_MEMORY_FACTS
except ImportError:
    MAX_MEMORY_FACTS = 20

_SCHEMA = """
CREATE TABLE IF NOT EXISTS projects (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    city       TEXT NOT NULL,
    project    TEXT NOT NULL,
    developer  TEXT DEFAULT '',
    config     TEXT DEFAULT '',
    carpet     TEXT DEFAULT '',
    price_sqft TEXT DEFAULT '',
    all_in     TEXT DEFAULT '',
    stage      TEXT DEFAULT '',
    basis      TEXT DEFAULT '',
    source_url TEXT DEFAULT '',
    updated_at REAL NOT NULL,
    UNIQUE(city, project)
);
CREATE TABLE IF NOT EXISTS corrections (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    city       TEXT NOT NULL,
    subject    TEXT NOT NULL,
    field      TEXT NOT NULL,
    value      TEXT NOT NULL,
    note       TEXT DEFAULT '',
    updated_at REAL NOT NULL,
    UNIQUE(city, subject, field)
);
"""


def _norm(s) -> str:
    return (s or "").strip()


def _key(s) -> str:
    return _norm(s).lower()


def _connect(db_path: str | None = None) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path or MEMORY_DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.executescript(_SCHEMA)  # idempotent; keeps every entry point self-initialising
    return conn


def init_db(db_path: str | None = None) -> None:
    with closing(_connect(db_path)) as conn:
        conn.commit()


def remember_projects(city: str, rows: list[dict], db_path: str | None = None) -> int:
    """Upsert verified project rows (keyed by city+project). Returns rows stored."""
    city_k = _key(city)
    stored = 0
    with closing(_connect(db_path)) as conn:
        for r in rows:
            project = _norm(r.get("project"))
            if not project or project.lower() in ("unknown", "project", "tbd", "-"):
                continue
            conn.execute(
                """
                INSERT INTO projects
                  (city, project, developer, config, carpet, price_sqft,
                   all_in, stage, basis, source_url, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(city, project) DO UPDATE SET
                  developer=excluded.developer, config=excluded.config,
                  carpet=excluded.carpet, price_sqft=excluded.price_sqft,
                  all_in=excluded.all_in, stage=excluded.stage,
                  basis=excluded.basis, source_url=excluded.source_url,
                  updated_at=excluded.updated_at
                """,
                (
                    city_k, project, _norm(r.get("developer")), _norm(r.get("config")),
                    _norm(r.get("carpet")), _norm(r.get("price_sqft")),
                    _norm(r.get("all_in")), _norm(r.get("stage")),
                    _norm(r.get("basis")), _norm(r.get("source_url")), time.time(),
                ),
            )
            stored += 1
        conn.commit()
    return stored


def recall_projects(city: str, db_path: str | None = None) -> list[dict]:
    with closing(_connect(db_path)) as conn:
        cur = conn.execute(
            "SELECT * FROM projects WHERE city=? ORDER BY updated_at DESC", (_key(city),)
        )
        return [dict(row) for row in cur.fetchall()]


def add_correction(
    city: str, subject: str, field: str, value: str, note: str = "", db_path: str | None = None
) -> None:
    with closing(_connect(db_path)) as conn:
        conn.execute(
            """
            INSERT INTO corrections (city, subject, field, value, note, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(city, subject, field) DO UPDATE SET
              value=excluded.value, note=excluded.note, updated_at=excluded.updated_at
            """,
            (_key(city), _norm(subject), _norm(field), _norm(value), _norm(note), time.time()),
        )
        conn.commit()


def recall_corrections(city: str, db_path: str | None = None) -> list[dict]:
    with closing(_connect(db_path)) as conn:
        cur = conn.execute(
            "SELECT * FROM corrections WHERE city=? ORDER BY updated_at DESC", (_key(city),)
        )
        return [dict(row) for row in cur.fetchall()]


def delete_correction(correction_id: int, db_path: str | None = None) -> None:
    with closing(_connect(db_path)) as conn:
        conn.execute("DELETE FROM corrections WHERE id=?", (correction_id,))
        conn.commit()


def _age(ts: float) -> str:
    days = max(0, int((time.time() - ts) / 86400))
    return "today" if days == 0 else f"{days}d ago"


def format_memory_block(city: str, db_path: str | None = None) -> tuple[str, str]:
    """Return (remembered_facts_text, corrections_text) for prompt injection."""
    projects = recall_projects(city, db_path)[:MAX_MEMORY_FACTS]
    corrections = recall_corrections(city, db_path)

    mem = ""
    if projects:
        mem = "\n".join(
            f"- [MEM] {p['project']}"
            + (f" ({p['developer']})" if p["developer"] else "")
            + f": config={p['config'] or '?'} | carpet={p['carpet'] or '?'} "
            f"| {p['price_sqft'] or '?'} | all-in={p['all_in'] or '?'} | {p['stage'] or '?'} "
            f"(recorded {_age(p['updated_at'])}, basis {p['basis'] or '?'})"
            for p in projects
        )

    corr = ""
    if corrections:
        corr = "\n".join(
            f"- {c['subject']} / {c['field']}: {c['value']}"
            + (f"  ({c['note']})" if c["note"] else "")
            for c in corrections
        )

    return mem, corr
