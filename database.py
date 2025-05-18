import sqlite3
import datetime

# Database filename
DB_NAME = "habits.db"

# Shared connection for in-memory database
_shared_conn = None


def connect_db():
    """
    Return a sqlite3 connection. If DB_NAME is ':memory:', reuse one global
    in-memory connection so that tables persist across calls.
    """
    global _shared_conn
    # Use shared connection for in-memory DB
    if DB_NAME == ":memory:":
        if _shared_conn is None:
            _shared_conn = sqlite3.connect(DB_NAME)
            _shared_conn.row_factory = sqlite3.Row
            _shared_conn.execute("PRAGMA foreign_keys = ON")
        return _shared_conn

    # Otherwise, create a fresh file-based connection
    try:
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row  # makes rows dict-like
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        raise ConnectionError(f"Couldn't connect to database: {e}")


def initialize_database():
    """
    Create tables for habits and completions if they don't exist.
    """
    conn = connect_db()
    # Create habits table
    conn.execute(
        '''
        CREATE TABLE IF NOT EXISTS habits (
            name TEXT PRIMARY KEY,
            description TEXT,
            schedule TEXT,
            created_on TEXT
        )
        '''
    )
    # Create completions table
    conn.execute(
        '''
        CREATE TABLE IF NOT EXISTS completions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            habit_name TEXT,
            completed_on TEXT,
            FOREIGN KEY (habit_name) REFERENCES habits(name) ON DELETE CASCADE
        )
        '''
    )
    conn.commit()


def add_habit_db(name, description, schedule, created_on):
    """
    Insert a new habit into the database.
    Raises QueryError on failure.
    """
    conn = None
    try:
        # Validate inputs
        if not name or name.strip() == "":
            raise ValueError("Name can't be empty")
        if schedule not in ("daily", "weekly"):
            raise ValueError("Schedule must be daily or weekly")

        conn = connect_db()
        conn.execute(
            "INSERT INTO habits VALUES (?, ?, ?, ?)",
            (name, description, schedule, created_on.isoformat())
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        if conn:
            conn.rollback()
        raise QueryError(f"Habit '{name}' already exists")
    except Exception as e:
        if conn:
            conn.rollback()
        raise QueryError(f"Failed to add habit: {e}")


def get_habit_db(name):
    """
    Retrieve a habit by name. Returns dict or None.
    """
    conn = None
    try:
        conn = connect_db()
        cursor = conn.execute(
            "SELECT * FROM habits WHERE name = ?", (name,)
        )
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None
    except Exception as e:
        raise QueryError(f"Failed to get habit: {e}")


def delete_habit_db(name):
    """
    Delete a habit by name. Returns True if deleted.
    """
    conn = None
    try:
        conn = connect_db()
        cursor = conn.execute(
            "DELETE FROM habits WHERE name = ?", (name,)
        )
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        if conn:
            conn.rollback()
        raise QueryError(f"Failed to delete habit: {e}")


def add_completion_db(habit_name, completed_on):
    """
    Log a completion for a habit.
    """
    conn = None
    try:
        conn = connect_db()
        conn.execute(
            "INSERT INTO completions (habit_name, completed_on) VALUES (?, ?)",
            (habit_name, completed_on.isoformat())
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        if conn:
            conn.rollback()
        raise QueryError(f"Completion already exists for '{habit_name}' at {completed_on}")
    except Exception as e:
        if conn:
            conn.rollback()
        raise QueryError(f"Failed to log completion: {e}")


def get_completions_db(habit_name):
    """
    Return list of completion datetimes for a habit.
    """
    conn = None
    try:
        conn = connect_db()
        cursor = conn.execute(
            "SELECT completed_on FROM completions WHERE habit_name = ? ORDER BY completed_on DESC",
            (habit_name,)
        )
        return [datetime.datetime.fromisoformat(row[0]) for row in cursor.fetchall()]
    except Exception as e:
        raise QueryError(f"Failed to get completions: {e}")


def get_completions_in_range_db(habit_name, start_date, end_date):
    """
    Return list of completion datetimes for a habit within [start_date, end_date].
    """
    conn = connect_db()
    cursor = conn.execute(
        "SELECT completed_on FROM completions "
        "WHERE habit_name = ? AND date(completed_on) BETWEEN ? AND ? "
        "ORDER BY completed_on DESC",
        (habit_name, start_date.isoformat(), end_date.isoformat())
    )
    return [datetime.datetime.fromisoformat(r[0]) for r in cursor.fetchall()]


def get_all_habits_db():
    """
    Return all habits as list of dicts, newest first.
    """
    conn = None
    try:
        conn = connect_db()
        cursor = conn.execute(
            "SELECT * FROM habits ORDER BY created_on DESC"
        )
        return [dict(row) for row in cursor.fetchall()]
    except Exception as e:
        raise QueryError(f"Failed to get habits: {e}")


# Custom exception for database queries
class QueryError(Exception):
    pass
