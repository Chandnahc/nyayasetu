import sqlite3
import json
from datetime import datetime

DB_PATH = "nyayasetu.db"

def init_db():
    """Create tables if they don't exist yet."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Stores each uploaded judgment
    c.execute("""
        CREATE TABLE IF NOT EXISTS judgments (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            filename    TEXT NOT NULL,
            uploaded_at TEXT NOT NULL,
            status      TEXT DEFAULT 'pending'
        )
    """)

    # Stores each extracted item from a judgment
    c.execute("""
        CREATE TABLE IF NOT EXISTS extracted_items (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            judgment_id     INTEGER NOT NULL,
            field_name      TEXT NOT NULL,
            ai_value        TEXT,
            verified_value  TEXT,
            confidence      TEXT,
            review_status   TEXT DEFAULT 'pending',
            FOREIGN KEY (judgment_id) REFERENCES judgments(id)
        )
    """)

    # Stores the final verified action plan
    c.execute("""
        CREATE TABLE IF NOT EXISTS action_plans (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            judgment_id     INTEGER NOT NULL,
            action_type     TEXT,
            description     TEXT,
            deadline        TEXT,
            department      TEXT,
            priority        TEXT,
            verified        INTEGER DEFAULT 0,
            FOREIGN KEY (judgment_id) REFERENCES judgments(id)
        )
    """)

    conn.commit()
    conn.close()


def save_judgment(filename):
    """Save a new judgment record, return its ID."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO judgments (filename, uploaded_at) VALUES (?, ?)",
        (filename, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )
    judgment_id = c.lastrowid
    conn.commit()
    conn.close()
    return judgment_id


def save_extracted_items(judgment_id, items: dict):
    """Save all AI-extracted fields for a judgment."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    for field_name, data in items.items():
        c.execute("""
            INSERT INTO extracted_items
                (judgment_id, field_name, ai_value, confidence)
            VALUES (?, ?, ?, ?)
        """, (
            judgment_id,
            field_name,
            str(data.get("value", "")),
            data.get("confidence", "medium")
        ))
    conn.commit()
    conn.close()


def save_action_plans(judgment_id, actions: list):
    """Save AI-generated action plan items."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    for action in actions:
        c.execute("""
            INSERT INTO action_plans
                (judgment_id, action_type, description, deadline, department, priority)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            judgment_id,
            action.get("action_type", ""),
            action.get("description", ""),
            action.get("deadline", "Not specified"),
            action.get("department", "Not specified"),
            action.get("priority", "Medium")
        ))
    conn.commit()
    conn.close()


def get_extracted_items(judgment_id):
    """Fetch all extracted items for a judgment."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "SELECT * FROM extracted_items WHERE judgment_id = ?",
        (judgment_id,)
    )
    rows = c.fetchall()
    conn.close()
    return rows


def get_action_plans(judgment_id):
    """Fetch action plan items for a judgment."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "SELECT * FROM action_plans WHERE judgment_id = ?",
        (judgment_id,)
    )
    rows = c.fetchall()
    conn.close()
    return rows


def verify_item(item_id, verified_value):
    """Officer approves/edits an extracted item."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        UPDATE extracted_items
        SET verified_value = ?, review_status = 'approved'
        WHERE id = ?
    """, (verified_value, item_id))
    conn.commit()
    conn.close()


def verify_action(action_id):
    """Officer approves an action plan item."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "UPDATE action_plans SET verified = 1 WHERE id = ?",
        (action_id,)
    )
    conn.commit()
    conn.close()


def get_all_judgments():
    """Fetch all judgments for the dashboard."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM judgments ORDER BY uploaded_at DESC")
    rows = c.fetchall()
    conn.close()
    return rows


def get_verified_actions_all():
    """Fetch all verified action plans across all judgments — for dashboard."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT ap.*, j.filename
        FROM action_plans ap
        JOIN judgments j ON ap.judgment_id = j.id
        WHERE ap.verified = 1
        ORDER BY ap.priority DESC
    """)
    rows = c.fetchall()
    conn.close()
    return rows
