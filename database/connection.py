"""
SQLite Database Connection Manager.
"""

import sqlite3
import os
from pathlib import Path
from contextlib import contextmanager
from config.settings import DATABASE_PATH, BASE_DIR

SCHEMA_PATH = BASE_DIR / "database" / "schema.sql"

def get_db_path() -> str:
    path = os.environ.get("AMAZON_DB_PATH", DATABASE_PATH)
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    return path

@contextmanager
def get_db_connection():
    """Context manager for SQLite connections with row factory and foreign keys."""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path, timeout=30.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_db(force: bool = False):
    """Initializes the SQLite schema if not already initialized."""
    db_path = get_db_path()
    with get_db_connection() as conn:
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            schema_sql = f.read()
        conn.executescript(schema_sql)
        
        # Populate initial data_sources registry if empty
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM data_sources")
        if cursor.fetchone()[0] == 0:
            sources = [
                ("amazon_in_manual", "Amazon India Web Pages (amazon.in)", "Web / Public URL", "Active", 1),
                ("google_trends", "Google Trends India (CSV Export)", "CSV Import", "Active", 1),
                ("google_keyword_planner", "Google Ads Keyword Planner (CSV Export)", "CSV Import", "Active", 1),
                ("keepa_manual", "Keepa Price & BSR Web Graph (Manual)", "Manual Observation", "Active", 1),
                ("keepa_api", "Keepa Product Data API", "REST API", "Disabled", 0),
                ("supplier_india", "Domestic India Sourcing (IndiaMART / Hubs)", "Quotation Manager", "Active", 1),
                ("supplier_overseas", "Overseas Sourcing (Alibaba / Global)", "Quotation Manager", "Active", 1),
            ]
            cursor.executemany(
                "INSERT INTO data_sources (source_key, source_name, source_type, status, is_free) VALUES (?, ?, ?, ?, ?)",
                sources
            )
