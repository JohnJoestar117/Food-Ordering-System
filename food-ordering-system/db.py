"""Database connection helpers. Every other module imports from here."""
import mysql.connector

try:
    from config import DB_CONFIG
except ImportError:
    raise SystemExit("config.py not found. Copy config.example.py to config.py and add your MySQL password.")


def get_connection(use_db=True):
    cfg = dict(DB_CONFIG)
    if not use_db:
        cfg.pop("database", None)
    return mysql.connector.connect(**cfg)


def run_query(sql, params=None, fetch=False):
    """Run one query. Returns rows if fetch=True, otherwise the last inserted id.
    Always pass values through `params` (%s placeholders) to prevent SQL injection."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(sql, params or ())
        if fetch:
            return cur.fetchall()
        conn.commit()
        return cur.lastrowid
    finally:
        cur.close()
        conn.close()
