import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import json

# Database connection parameters
DB_PARAMS = {
    "dbname": "mirror",
    "user": "postgres",
    "password": "1234!",
    "host": "localhost",
    "port": "5432"
}

def setup_database():
    """Create tables for infrastructure data"""
    conn = psycopg2.connect(**DB_PARAMS)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()

    print("Setting up database...")

    # Create airports table with JSONB geometry
    cur.execute("""
        DROP TABLE IF EXISTS airports CASCADE;
        CREATE TABLE airports (
            id VARCHAR(255) PRIMARY KEY,
            name VARCHAR(255),
            subtype VARCHAR(100),
            class VARCHAR(100),
            geometry JSONB
        );
    """)
    print("✓ Created airports table")

    # Create ports table with JSONB geometry
    cur.execute("""
        DROP TABLE IF EXISTS ports CASCADE;
        CREATE TABLE ports (
            id VARCHAR(255) PRIMARY KEY,
            name VARCHAR(255),
            subtype VARCHAR(100),
            class VARCHAR(100),
            geometry JSONB
        );
    """)
    print("✓ Created ports table")

    # Create warehouses table with JSONB geometry
    cur.execute("""
        DROP TABLE IF EXISTS warehouses CASCADE;
        CREATE TABLE warehouses (
            id VARCHAR(255) PRIMARY KEY,
            name VARCHAR(255),
            subtype VARCHAR(100),
            class VARCHAR(100),
            height FLOAT,
            num_floors INTEGER,
            geometry JSONB
        );
    """)
    print("✓ Created warehouses table")

    # Create transportation_buildings table with JSONB geometry
    cur.execute("""
        DROP TABLE IF EXISTS transportation_buildings CASCADE;
        CREATE TABLE transportation_buildings (
            id VARCHAR(255) PRIMARY KEY,
            name VARCHAR(255),
            subtype VARCHAR(100),
            class VARCHAR(100),
            height FLOAT,
            num_floors INTEGER,
            geometry JSONB
        );
    """)
    print("✓ Created transportation_buildings table")

    # Create indices
    cur.execute("CREATE INDEX idx_airports_subtype ON airports(subtype);")
    cur.execute("CREATE INDEX idx_airports_class ON airports(class);")
    cur.execute("CREATE INDEX idx_ports_subtype ON ports(subtype);")
    cur.execute("CREATE INDEX idx_ports_class ON ports(class);")
    cur.execute("CREATE INDEX idx_warehouses_class ON warehouses(class);")
    cur.execute("CREATE INDEX idx_transportation_buildings_class ON transportation_buildings(class);")
    print("✓ Created indices")

    cur.close()
    conn.close()
    print("\n✓ Database setup complete!")

def load_geojson_to_postgres(geojson_file, table_name, has_building_attrs=False):
    """Load GeoJSON data into PostgreSQL table"""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()

    print(f"\nLoading {geojson_file} into {table_name}...")

    with open(geojson_file, 'r') as f:
        data = json.load(f)

    features = data.get('features', [])
    inserted = 0

    for feature in features:
        props = feature.get('properties', {})
        geom = feature.get('geometry')

        if not geom:
            continue

        # Store geometry as JSONB
        geom_json = json.dumps(geom)

        try:
            if has_building_attrs:
                # Buildings table with height and num_floors
                cur.execute(f"""
                    INSERT INTO {table_name} (id, name, subtype, class, height, num_floors, geometry)
                    VALUES (%s, %s, %s, %s, %s, %s, %s::jsonb)
                    ON CONFLICT (id) DO NOTHING;
                """, (
                    props.get('id'),
                    props.get('name'),
                    props.get('subtype'),
                    props.get('class'),
                    props.get('height'),
                    props.get('num_floors'),
                    geom_json
                ))
            else:
                # Infrastructure table without height/num_floors
                cur.execute(f"""
                    INSERT INTO {table_name} (id, name, subtype, class, geometry)
                    VALUES (%s, %s, %s, %s, %s::jsonb)
                    ON CONFLICT (id) DO NOTHING;
                """, (
                    props.get('id'),
                    props.get('name'),
                    props.get('subtype'),
                    props.get('class'),
                    geom_json
                ))
            inserted += 1
        except Exception as e:
            print(f"Error inserting feature: {e}")
            continue

    conn.commit()
    cur.close()
    conn.close()

    print(f"✓ Inserted {inserted} features into {table_name}")

if __name__ == "__main__":
    # Setup database
    setup_database()

    # Load infrastructure data (no building attributes)
    load_geojson_to_postgres(
        'app/public/data/la_airport_infrastructure.geojson',
        'airports',
        has_building_attrs=False
    )
    load_geojson_to_postgres(
        'app/public/data/la_port_infrastructure.geojson',
        'ports',
        has_building_attrs=False
    )

    # Load building data (with height and num_floors)
    load_geojson_to_postgres(
        'app/public/data/la_warehouses.geojson',
        'warehouses',
        has_building_attrs=True
    )
    load_geojson_to_postgres(
        'app/public/data/la_transportation_buildings.geojson',
        'transportation_buildings',
        has_building_attrs=True
    )

    print("\n✓ All data loaded successfully!")
