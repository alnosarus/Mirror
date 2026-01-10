"""
Database connection module
"""
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager

DB_CONFIG = {
    "dbname": "mirror",
    "user": "postgres",
    "password": "1234!",
    "host": "localhost",
    "port": "5432"
}

@contextmanager
def get_db_connection():
    """
    Context manager for database connections
    Usage:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM facilities")
            ...
    """
    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)
        yield conn
        conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if conn:
            conn.close()
