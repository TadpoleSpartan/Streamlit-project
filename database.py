import sqlite3
from pathlib import Path
import hashlib
from datetime import datetime

DATABASE_PATH = Path(__file__).parent / "data" / "quizmaster.db"

def get_connection():
    """Get a database connection."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    return conn

def init_database():
    """Create all tables if they don't exist."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            is_admin BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Questions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            question TEXT NOT NULL,
            options TEXT NOT NULL,
            correct_index INTEGER NOT NULL,
            difficulty TEXT DEFAULT 'medium',
            points INTEGER DEFAULT 10,
            created_by INTEGER REFERENCES users(id),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Scores table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER REFERENCES users(id),
            category TEXT,
            score INTEGER,
            correct_answers INTEGER,
            total_questions INTEGER,
            played_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()

def hash_password(password: str) -> str:
    """Hash a password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(username: str, password: str, is_admin: bool = False) -> bool:
    """Create a new user. Returns True if successful."""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO users (username, password_hash, is_admin) VALUES (?, ?, ?)",
            (username, hash_password(password), is_admin)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # Username already exists
    finally:
        conn.close()

def verify_user(username: str, password: str):
    """Verify username and password. Returns user dict or None."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT * FROM users WHERE username = ? AND password_hash = ?",
        (username, hash_password(password))
    )
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return dict(row)
    return None

def get_questions_by_category(category: str) -> list:
    """Get all questions for a category."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT * FROM questions WHERE category = ?",
        (category,)
    )
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]

def get_all_categories() -> list:
    """Get list of all unique categories."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT DISTINCT category FROM questions")
    
    rows = cursor.fetchall()
    conn.close()
    
    return [row["category"] for row in rows]

def add_question(category: str, question: str, options: list, 
                 correct_index: int, difficulty: str = "medium",
                 points: int = 10, created_by: int = None) -> int:
    """Add a new question. Returns the new question ID."""
    import json
    
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO questions 
        (category, question, options, correct_index, difficulty, points, created_by)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (category, question, json.dumps(options), correct_index, 
          difficulty, points, created_by))
    
    question_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return question_id

def save_score(user_id: int, category: str, score: int, 
               correct: int, total: int):
    """Save a game score."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO scores (user_id, category, score, correct_answers, total_questions)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, category, score, correct, total))
    
    conn.commit()
    conn.close()

def get_highscores(limit: int = 10) -> list:
    """Get top scores."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT s.*, u.username 
        FROM scores s
        JOIN users u ON s.user_id = u.id
        ORDER BY s.score DESC
        LIMIT ?
    """, (limit,))
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]

# Initialize the database when this module is imported
init_database()
