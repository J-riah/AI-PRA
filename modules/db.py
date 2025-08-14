import sqlite3
from typing import List, Tuple, Optional

SCHEMA = """
CREATE TABLE IF NOT EXISTS analyses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    resume_text TEXT,
    job_desc TEXT,
    score REAL,
    matched_keywords TEXT,
    missing_keywords TEXT,
    file_name TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
"""

def init_db(db_path: str):
    conn = sqlite3.connect(db_path)
    try:
        conn.execute(SCHEMA)
        conn.commit()
    finally:
        conn.close()

def insert_analysis(
    db_path: str,
    resume_text: str,
    job_desc: str,
    score: float,
    matched_keywords: str,
    missing_keywords: str,
    file_name: str = None
):
    conn = sqlite3.connect(db_path)
    try:
        conn.execute(
            "INSERT INTO analyses (resume_text, job_desc, score, matched_keywords, missing_keywords, file_name) VALUES (?, ?, ?, ?, ?, ?)",
            (resume_text, job_desc, score, matched_keywords, missing_keywords, file_name)
        )
        conn.commit()
    finally:
        conn.close()

def fetch_history(db_path: str, limit: int = 20) -> List[Tuple[int, float, str, str]]:
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.execute(
            "SELECT id, score, timestamp, file_name FROM analyses ORDER BY id DESC LIMIT ?",
            (limit,)
        )
        return list(cur.fetchall())
    finally:
        conn.close()
