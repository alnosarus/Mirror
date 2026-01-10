from flask import Flask, jsonify
from flask_cors import CORS
import psycopg2
import psycopg2.extras
import json

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Database connection parameters
DB_PARAMS = {
    "dbname": "mirror",
    "user": "postgres",
    "password": "1234!",
    "host": "localhost",
    "port": "5432"
}

def get_db_connection():
    """Create a database connection"""
    return psycopg2.connect(**DB_PARAMS)

@app.route('/api/airports', methods=['GET'])
def get_airports():
    """Get all airports as GeoJSON"""
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cur.execute("""
            SELECT id, name, subtype, class, geometry
            FROM airports
        """)

        rows = cur.fetchall()

        # Convert to GeoJSON format
        features = []
        for row in rows:
            features.append({
                "type": "Feature",
                "properties": {
                    "id": row['id'],
                    "name": row['name'],
                    "subtype": row['subtype'],
                    "class": row['class']
                },
                "geometry": row['geometry']  # Already in JSON format
            })

        geojson = {
            "type": "FeatureCollection",
            "features": features
        }

        cur.close()
        conn.close()

        return jsonify(geojson)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/ports', methods=['GET'])
def get_ports():
    """Get all ports as GeoJSON"""
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cur.execute("""
            SELECT id, name, subtype, class, geometry
            FROM ports
        """)

        rows = cur.fetchall()

        # Convert to GeoJSON format
        features = []
        for row in rows:
            features.append({
                "type": "Feature",
                "properties": {
                    "id": row['id'],
                    "name": row['name'],
                    "subtype": row['subtype'],
                    "class": row['class']
                },
                "geometry": row['geometry']  # Already in JSON format
            })

        geojson = {
            "type": "FeatureCollection",
            "features": features
        }

        cur.close()
        conn.close()

        return jsonify(geojson)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    print("Starting API server on http://localhost:5001")
    print("Endpoints:")
    print("  - GET /api/airports")
    print("  - GET /api/ports")
    print("  - GET /api/health")
    app.run(debug=True, port=5001)
