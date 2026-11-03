
import sqlite3
import json
from datetime import datetime

DB_NAME = "resume_analyzer.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def initialize_database():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                target_role TEXT NOT NULL,
                resume_filename TEXT,
                job_description TEXT,
                match_score INTEGER,
                matched_skills TEXT,
                missing_skills TEXT,
                created_at TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS interview_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                target_role TEXT NOT NULL,
                question TEXT NOT NULL,
                user_answer TEXT NOT NULL,
                feedback TEXT,
                score REAL,
                created_at TEXT NOT NULL
            )
        """)

def save_analysis(
    name,
    email,
    target_role,
    resume_filename,
    job_description,
    result
):
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO analyses (
                name,
                email,
                target_role,
                resume_filename,
                job_description,
                match_score,
                matched_skills,
                missing_skills,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            name,
            email,
            target_role,
            resume_filename,
            job_description,
            result["match_score"],
            json.dumps(result["matched_skills"]),
            json.dumps(result["missing_skills"]),
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))


def get_analysis_history(email):
    with get_connection() as conn:
        cursor = conn.execute("""
            SELECT
                id,
                target_role,
                resume_filename,
                match_score,
                matched_skills,
                missing_skills,
                created_at
            FROM analyses
            WHERE email = ?
            ORDER BY id DESC
        """, (email,))

        rows = cursor.fetchall()

    history = []

    for row in rows:
        history.append({
            "Analysis ID": row[0],
            "Target Role": row[1],
            "Resume": row[2],
            "Match Score (%)": row[3],
            "Matched Skills": ", ".join(json.loads(row[4])),
            "Missing Skills": ", ".join(json.loads(row[5])),
            "Date": row[6]
        })

    return history


def save_interview_result(
    email,
    target_role,
    question,
    user_answer,
    feedback,
    score
):
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO interview_history (
                email,
                target_role,
                question,
                user_answer,
                feedback,
                score,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            email,
            target_role,
            question,
            user_answer,
            feedback,
            score,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))


def get_interview_history(email):
    with get_connection() as conn:
        cursor = conn.execute("""
            SELECT
                id,
                target_role,
                question,
                score,
                created_at
            FROM interview_history
            WHERE email = ?
            ORDER BY id DESC
        """, (email,))

        return cursor.fetchall()
