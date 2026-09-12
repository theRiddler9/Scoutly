"""
Scoutly — SQLite Database Setup & Connection
"""

import aiosqlite
import json
from datetime import datetime
from app.config import DATABASE_PATH

# ── Schema ─────────────────────────────────────────────────────────────────────

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    github_url TEXT DEFAULT '',
    skills TEXT DEFAULT '[]',          -- JSON array of strings
    projects TEXT DEFAULT '[]',        -- JSON array of {title, description, tech_stack}
    resume_text TEXT DEFAULT '',
    social_handles TEXT DEFAULT '{}',  -- JSON {twitter, linkedin, website}
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS opportunities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    source_url TEXT DEFAULT '',
    apply_url TEXT DEFAULT '',
    deadline TEXT DEFAULT '',
    eligibility_summary TEXT DEFAULT '',
    prize_info TEXT DEFAULT '',
    raw_text TEXT DEFAULT '',
    description TEXT DEFAULT '',
    organizer TEXT DEFAULT '',
    tags TEXT DEFAULT '[]',            -- JSON array
    url_hash TEXT UNIQUE,              -- SHA256 of apply_url for dedup
    status TEXT DEFAULT 'found',       -- found | matched | archived
    discovered_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS matches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    profile_id INTEGER NOT NULL,
    opportunity_id INTEGER NOT NULL,
    qualifies INTEGER DEFAULT 0,       -- boolean as int
    score INTEGER DEFAULT 0,           -- 0-100
    reasoning TEXT DEFAULT '',
    deadline_feasible INTEGER DEFAULT 1,
    matched_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (profile_id) REFERENCES profiles(id),
    FOREIGN KEY (opportunity_id) REFERENCES opportunities(id),
    UNIQUE(profile_id, opportunity_id)
);

CREATE TABLE IF NOT EXISTS applications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    match_id INTEGER NOT NULL,
    status TEXT DEFAULT 'pending',     -- pending | filling | filled | awaiting_approval | approved | submitted | failed
    form_data TEXT DEFAULT '{}',       -- JSON of filled fields
    screenshot_path TEXT DEFAULT '',
    error_message TEXT DEFAULT '',
    filled_at TEXT,
    approved_at TEXT,
    submitted_at TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (match_id) REFERENCES matches(id)
);

CREATE TABLE IF NOT EXISTS field_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    application_id INTEGER NOT NULL,
    field_label TEXT NOT NULL,
    field_type TEXT DEFAULT '',
    filled_value TEXT DEFAULT '',
    reasoning TEXT DEFAULT '',
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (application_id) REFERENCES applications(id)
);

CREATE INDEX IF NOT EXISTS idx_opportunities_status ON opportunities(status);
CREATE INDEX IF NOT EXISTS idx_opportunities_deadline ON opportunities(deadline);
CREATE INDEX IF NOT EXISTS idx_matches_score ON matches(score DESC);
CREATE INDEX IF NOT EXISTS idx_applications_status ON applications(status);
"""


# ── Connection Helpers ─────────────────────────────────────────────────────────

async def get_db() -> aiosqlite.Connection:
    """Get a database connection with row factory enabled."""
    db = await aiosqlite.connect(DATABASE_PATH)
    db.row_factory = aiosqlite.Row
    await db.execute("PRAGMA journal_mode=WAL")
    await db.execute("PRAGMA foreign_keys=ON")
    return db


async def init_db():
    """Initialize the database schema."""
    db = await get_db()
    try:
        await db.executescript(SCHEMA_SQL)
        await db.commit()
    finally:
        await db.close()


async def fetch_one(query: str, params: tuple = ()) -> dict | None:
    """Execute a query and return a single row as a dict."""
    db = await get_db()
    try:
        cursor = await db.execute(query, params)
        row = await cursor.fetchone()
        if row is None:
            return None
        return dict(row)
    finally:
        await db.close()


async def fetch_all(query: str, params: tuple = ()) -> list[dict]:
    """Execute a query and return all rows as a list of dicts."""
    db = await get_db()
    try:
        cursor = await db.execute(query, params)
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        await db.close()


async def execute_insert(query: str, params: tuple = ()) -> int:
    """Execute an INSERT and return the last row ID."""
    db = await get_db()
    try:
        cursor = await db.execute(query, params)
        await db.commit()
        return cursor.lastrowid
    finally:
        await db.close()


async def execute_update(query: str, params: tuple = ()) -> int:
    """Execute an UPDATE/DELETE and return rows affected."""
    db = await get_db()
    try:
        cursor = await db.execute(query, params)
        await db.commit()
        return cursor.rowcount
    finally:
        await db.close()
