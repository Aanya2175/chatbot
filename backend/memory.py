import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "celiac_data.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS conversations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT, role TEXT, content TEXT,
        intent TEXT, timestamp TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS symptoms (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT, symptom TEXT,
        severity INTEGER, timestamp TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS meals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT, meal TEXT,
        gluten_free INTEGER DEFAULT 1, timestamp TEXT
    )''')
    conn.commit()
    conn.close()
    
def save_meal(session_id: str, meal: str):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO meals VALUES (NULL,?,?,?,?)",
        (session_id, meal, 1, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()

def get_meals(session_id: str):
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT meal, timestamp FROM meals WHERE session_id=? ORDER BY id DESC LIMIT 30",
        (session_id,)
    ).fetchall()
    conn.close()
    return [{"meal": r[0], "timestamp": r[1]} for r in rows]

def save_message(session_id, role, content, intent="general"):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO conversations VALUES (NULL,?,?,?,?,?)",
        (session_id, role, content, intent, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()

def get_history(session_id, limit=10):
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT role, content FROM conversations WHERE session_id=? ORDER BY id DESC LIMIT ?",
        (session_id, limit)
    ).fetchall()
    conn.close()
    return [{"role": r[0], "content": r[1]} for r in reversed(rows)]

def save_symptom(session_id, symptom, severity=5):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO symptoms VALUES (NULL,?,?,?,?)",
        (session_id, symptom, severity, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()

def get_symptoms(session_id):
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT symptom, severity, timestamp FROM symptoms WHERE session_id=? ORDER BY id DESC LIMIT 30",
        (session_id,)
    ).fetchall()
    conn.close()
    return [{"symptom": r[0], "severity": r[1], "timestamp": r[2]} for r in rows]
# Temporary store for pending symptom severity questions
_pending_symptoms = {}

def set_pending_symptom(session_id: str, symptom: str):
    _pending_symptoms[session_id] = symptom

def get_pending_symptom(session_id: str):
    return _pending_symptoms.get(session_id)

def clear_pending_symptom(session_id: str):
    _pending_symptoms.pop(session_id, None)