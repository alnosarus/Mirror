"""
Setup Mirror database with PostGIS - Simplified version
Works with default Homebrew PostgreSQL (no password)
"""
import psycopg2
from psycopg2 import sql
import os

# Try different connection methods
def get_connection():
    """Try to connect to PostgreSQL using different methods"""

    # Method 1: Homebrew PostgreSQL (no password, current user)
    try:
        conn = psycopg2.connect(
            dbname="postgres",
            user=os.getenv('USER'),  # Current macOS user
            host="/tmp"  # Unix socket
        )
        print(f"✓ Connected via Homebrew PostgreSQL (user: {os.getenv('USER')})")
        return conn
    except Exception as e1:
        print(f"✗ Homebrew connection failed: {e1}")

        # Method 2: PostgreSQL with password (your original setup)
        try:
            conn = psycopg2.connect(
                dbname="postgres",
                user="postgres",
                password="1234!",
                host="localhost",
                port="5432"
            )
            print("✓ Connected via localhost PostgreSQL (user: postgres)")
            return conn
        except Exception as e2:
            print(f"✗ Localhost connection failed: {e2}")
            return None

def create_mirror_database(conn):
    """Create the mirror database if it doesn't exist"""
    try:
        conn.autocommit = True
        cursor = conn.cursor()

        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname='mirror'")
        exists = cursor.fetchone()

        if not exists:
            cursor.execute(sql.SQL("CREATE DATABASE {}").format(
                sql.Identifier('mirror')
            ))
            print("✓ Created 'mirror' database")
        else:
            print("✓ 'mirror' database already exists")

        cursor.close()
        return True
    except Exception as e:
        print(f"✗ Failed to create database: {e}")
        return False

def enable_postgis(user, host="/tmp", password=None):
    """Enable PostGIS extension in mirror database"""
    try:
        # Connect to mirror database
        if password:
            conn = psycopg2.connect(
                dbname='mirror',
                user=user,
                password=password,
                host='localhost',
                port='5432'
            )
        else:
            conn = psycopg2.connect(
                dbname='mirror',
                user=user,
                host=host
            )

        cursor = conn.cursor()

        # Enable PostGIS
        cursor.execute("CREATE EXTENSION IF NOT EXISTS postgis;")
        conn.commit()
        print("✓ PostGIS extension enabled")

        # Verify PostGIS version
        cursor.execute("SELECT PostGIS_version();")
        version = cursor.fetchone()
        print(f"✓ PostGIS version: {version[0]}")

        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"✗ Failed to enable PostGIS: {e}")
        return False

def create_sample_table(user, host="/tmp", password=None):
    """Create a sample infrastructure table to test PostGIS"""
    try:
        if password:
            conn = psycopg2.connect(
                dbname='mirror',
                user=user,
                password=password,
                host='localhost',
                port='5432'
            )
        else:
            conn = psycopg2.connect(
                dbname='mirror',
                user=user,
                host=host
            )

        cursor = conn.cursor()

        # Create infrastructure table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS infrastructure (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                type VARCHAR(100) NOT NULL,
                geom GEOMETRY(Point, 4326),
                properties JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # Create spatial index
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS infrastructure_geom_idx
            ON infrastructure USING GIST (geom);
        """)

        conn.commit()
        print("✓ Created 'infrastructure' table with PostGIS geometry column")

        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"✗ Failed to create table: {e}")
        return False

if __name__ == "__main__":
    print("=== Mirror Database Setup ===\n")

    # Get connection
    conn = get_connection()

    if not conn:
        print("\n✗ Could not connect to PostgreSQL")
        print("\nPlease ensure PostgreSQL is running:")
        print("  - Homebrew: brew services start postgresql@17")
        print("  - Or your existing PostgreSQL service")
        exit(1)

    # Get connection details for reuse
    user = conn.info.user
    host = conn.info.host if conn.info.host else "/tmp"
    password = "1234!" if user == "postgres" else None

    print(f"\n=== Creating Mirror Database ===\n")
    if create_mirror_database(conn):
        conn.close()

        print(f"\n=== Enabling PostGIS ===\n")
        if enable_postgis(user, host, password):
            print(f"\n=== Creating Sample Tables ===\n")
            if create_sample_table(user, host, password):
                print("\n✅ Database setup complete!")
                print(f"\nConnection details:")
                print(f"  Database: mirror")
                print(f"  User: {user}")
                print(f"  Host: {host}")
                if password:
                    print(f"  Password: {password}")
            else:
                print("\n✗ Table creation failed")
        else:
            print("\n✗ PostGIS setup failed")
    else:
        print("\n✗ Database creation failed")
        conn.close()
