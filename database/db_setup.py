"""
database/db_setup.py
---------------------
All SQLite access for the prediction-history feature lives here.

Keeping database logic isolated from app.py means:
  - app.py stays focused on routing/HTTP concerns
  - the storage layer can be swapped later (e.g. to Postgres) by editing only
    this file

Table schema:
    predictions(
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        text         TEXT NOT NULL,
        language     TEXT NOT NULL,
        prediction   TEXT NOT NULL,
        confidence   REAL NOT NULL,
        probabilities TEXT NOT NULL,   -- JSON string, e.g. {"Positive":0.98,"Negative":0.02}
        created_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
    )
"""

import os
import sqlite3

# Absolute path to database/history.db, regardless of the working directory
# the app is launched from.
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "history.db")


def get_connection():
    """Returns a new SQLite connection with row access by column name."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Creates the predictions table if it does not already exist.
    Safe to call every time the app starts."""
    conn = get_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS predictions (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            text          TEXT NOT NULL,
            language      TEXT NOT NULL,
            prediction    TEXT NOT NULL,
            confidence    REAL NOT NULL,
            probabilities TEXT NOT NULL,
            created_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()
    conn.close()


def insert_prediction(text, language, prediction, confidence, probabilities):
    """Inserts a new prediction record and returns its generated id."""
    conn = get_connection()
    cursor = conn.execute(
        """
        INSERT INTO predictions (text, language, prediction, confidence, probabilities)
        VALUES (?, ?, ?, ?, ?)
        """,
        (text, language, prediction, confidence, probabilities),
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id


def get_record_by_id(record_id):
    """Fetches a single prediction record by its id. Returns None if missing."""
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM predictions WHERE id = ?", (record_id,)
    ).fetchone()
    conn.close()
    return row


def _build_filters(search_query, language_filter):
    """Builds a shared WHERE clause + params list for search/filter reuse
    across get_history, count_history, and get_all_records_for_export."""
    clauses = []
    params = []

    if search_query:
        clauses.append("text LIKE ?")
        params.append(f"%{search_query}%")

    if language_filter:
        clauses.append("language = ?")
        params.append(language_filter)

    where_clause = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    return where_clause, params


def get_history(search_query, language_filter, page, per_page):
    """Returns one page of prediction records, newest first."""
    where_clause, params = _build_filters(search_query, language_filter)
    offset = (page - 1) * per_page

    conn = get_connection()
    rows = conn.execute(
        f"""
        SELECT * FROM predictions
        {where_clause}
        ORDER BY created_at DESC
        LIMIT ? OFFSET ?
        """,
        (*params, per_page, offset),
    ).fetchall()
    conn.close()
    return rows


def count_history(search_query, language_filter):
    """Returns the total number of records matching the current search/filter,
    used to calculate pagination."""
    where_clause, params = _build_filters(search_query, language_filter)

    conn = get_connection()
    total = conn.execute(
        f"SELECT COUNT(*) AS total FROM predictions {where_clause}", params
    ).fetchone()["total"]
    conn.close()
    return total


def delete_record(record_id):
    """Deletes a single prediction record by id."""
    conn = get_connection()
    conn.execute("DELETE FROM predictions WHERE id = ?", (record_id,))
    conn.commit()
    conn.close()


def get_all_records_for_export(search_query, language_filter):
    """Returns ALL matching records (no pagination) for CSV export."""
    where_clause, params = _build_filters(search_query, language_filter)

    conn = get_connection()
    rows = conn.execute(
        f"""
        SELECT * FROM predictions
        {where_clause}
        ORDER BY created_at DESC
        """,
        params,
    ).fetchall()
    conn.close()
    return rows
