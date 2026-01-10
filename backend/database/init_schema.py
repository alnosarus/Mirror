"""
Initialize Mirror database schema
"""
import psycopg2

DB_CONFIG = {
    "dbname": "mirror",
    "user": "postgres",
    "password": "1234!",
    "host": "localhost",
    "port": "5432"
}

def init_schema():
    """Initialize database schema"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Read schema file
        with open('database/schema.sql', 'r') as f:
            schema_sql = f.read()

        # Execute schema
        cursor.execute(schema_sql)
        conn.commit()

        print("✓ Database schema created successfully")

        # Verify tables
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)

        tables = cursor.fetchall()
        print(f"\n✓ Created {len(tables)} tables:")
        for table in tables:
            print(f"  - {table[0]}")

        # Check sample data
        cursor.execute("SELECT COUNT(*) FROM facilities;")
        facility_count = cursor.fetchone()[0]
        print(f"\n✓ Inserted {facility_count} sample facilities")

        cursor.execute("SELECT COUNT(*) FROM supply_chain_connections;")
        connection_count = cursor.fetchone()[0]
        print(f"✓ Inserted {connection_count} supply chain connections")

        cursor.execute("SELECT COUNT(*) FROM simulations;")
        sim_count = cursor.fetchone()[0]
        print(f"✓ Inserted {sim_count} sample simulation(s)")

        cursor.close()
        conn.close()

        return True

    except Exception as e:
        print(f"✗ Schema initialization failed: {e}")
        return False

if __name__ == "__main__":
    print("=== Initializing Mirror Database Schema ===\n")
    if init_schema():
        print("\n✅ Database initialization complete!")
    else:
        print("\n✗ Database initialization failed")
