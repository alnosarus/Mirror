from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
import psycopg2.extras
import json
import os
import requests
from anthropic import Anthropic

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize Anthropic client
anthropic_client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

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

@app.route('/api/warehouses', methods=['GET'])
def get_warehouses():
    """Get all warehouses as GeoJSON"""
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cur.execute("""
            SELECT id, name, subtype, class, height, num_floors, geometry
            FROM warehouses
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
                    "class": row['class'],
                    "height": row['height'],
                    "num_floors": row['num_floors']
                },
                "geometry": row['geometry']
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

@app.route('/api/chat', methods=['POST'])
def chat():
    """Chat with Claude agent about infrastructure data"""
    try:
        data = request.json
        user_message = data.get('message', '')
        conversation_history = data.get('history', [])

        if not user_message:
            return jsonify({"error": "No message provided"}), 400

        # Get current infrastructure stats for context
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # Quick stats query
        cur.execute("SELECT COUNT(*) as count FROM airports")
        airport_count = cur.fetchone()['count']

        cur.execute("SELECT COUNT(*) as count FROM ports")
        port_count = cur.fetchone()['count']

        cur.execute("SELECT COUNT(*) as count FROM warehouses")
        warehouse_count = cur.fetchone()['count']

        cur.close()
        conn.close()

        # Define tools that Claude can use
        tools = [
            {
                "name": "fly_to_location",
                "description": "Moves the map camera to a specific location with optional zoom and pitch. Use this when the user wants to navigate to a specific place, infrastructure, or coordinates.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "longitude": {"type": "number", "description": "Longitude coordinate"},
                        "latitude": {"type": "number", "description": "Latitude coordinate"},
                        "zoom": {"type": "number", "description": "Zoom level (8-18, default 14)"},
                        "pitch": {"type": "number", "description": "Camera pitch/tilt in degrees (0-60, default 50)"},
                        "bearing": {"type": "number", "description": "Camera bearing/rotation in degrees (default 0)"},
                        "duration": {"type": "number", "description": "Animation duration in milliseconds (default 2000)"}
                    },
                    "required": ["longitude", "latitude"]
                }
            },
            {
                "name": "filter_infrastructure",
                "description": "Filters visible infrastructure by type and optionally by specific properties. Use this when user wants to see only certain types of infrastructure.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "types": {
                            "type": "array",
                            "items": {"type": "string", "enum": ["airports", "ports", "warehouses"]},
                            "description": "Which infrastructure types to show"
                        },
                        "airport_classes": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Specific airport classes to show (e.g., 'airport', 'helipad', 'terminal')"
                        },
                        "port_subtypes": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Specific port subtypes to show (e.g., 'quay', 'pier')"
                        }
                    },
                    "required": ["types"]
                }
            },
            {
                "name": "highlight_feature",
                "description": "Highlights a specific infrastructure feature on the map by its name or ID. Use this when the user wants to see or focus on a specific building or facility.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Name of the infrastructure to highlight"},
                        "type": {"type": "string", "enum": ["airport", "port", "warehouse"], "description": "Type of infrastructure"}
                    },
                    "required": ["name", "type"]
                }
            },
            {
                "name": "calculate_route",
                "description": "Calculates a driving route between two locations and displays it on the map with distance and time estimates. Use this when the user wants directions or route information between two points.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "start": {
                            "type": "object",
                            "properties": {
                                "lat": {"type": "number", "description": "Start latitude"},
                                "lon": {"type": "number", "description": "Start longitude"}
                            },
                            "required": ["lat", "lon"],
                            "description": "Starting location coordinates"
                        },
                        "end": {
                            "type": "object",
                            "properties": {
                                "lat": {"type": "number", "description": "End latitude"},
                                "lon": {"type": "number", "description": "End longitude"}
                            },
                            "required": ["lat", "lon"],
                            "description": "Destination coordinates"
                        }
                    },
                    "required": ["start", "end"]
                }
            },
            {
                "name": "find_nearest",
                "description": "Finds the nearest infrastructure feature of a specific type to a given location. Use this when the user asks for the closest/nearest airport, port, or warehouse to a location.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "object",
                            "properties": {
                                "lat": {"type": "number", "description": "Reference latitude"},
                                "lon": {"type": "number", "description": "Reference longitude"}
                            },
                            "required": ["lat", "lon"],
                            "description": "Location to search from"
                        },
                        "infrastructure_type": {
                            "type": "string",
                            "enum": ["airports", "ports", "warehouses"],
                            "description": "Type of infrastructure to search for"
                        }
                    },
                    "required": ["location", "infrastructure_type"]
                }
            }
        ]

        # System prompt with context
        system_prompt = f"""You are an AI assistant helping users explore infrastructure data for the Los Angeles area in a 3D visualization application.

Current data overview:
- Airports: {airport_count} features (including airports, helipads, terminals)
- Ports: {port_count} features (quays, piers, and other port infrastructure)
- Warehouses: {warehouse_count} buildings

You have access to tools that can:
1. Move the camera to specific locations (fly_to_location)
2. Filter what infrastructure is visible (filter_infrastructure)
3. Highlight specific features (highlight_feature)
4. Calculate routes between locations (calculate_route)
5. Find nearest infrastructure to a location (find_nearest)

IMPORTANT Guidelines:
- For simple data questions (e.g., "How many airports?"), answer DIRECTLY using the counts above. DO NOT use tools.
- For navigation/action requests, use the appropriate tool.
- If a user requests a feature or action that you CANNOT do with the available tools, politely respond with: "Sorry, that feature is not yet implemented. Currently, I can help you with navigation, route planning, filtering infrastructure, and finding nearest locations."

Examples of what you CAN do:
- "How many airports?" → Answer: "There are {airport_count} airport infrastructure features..."
- "Take me to LAX" → Use fly_to_location tool
- "Show only airports" → Use filter_infrastructure tool
- "Route from LAX to Long Beach Port" → Use calculate_route tool
- "What's the closest warehouse to LAX?" → Use find_nearest tool

Examples of what you CANNOT do (respond with "not yet implemented"):
- Editing data, adding new infrastructure, deleting features
- Weather information, traffic cameras, live updates
- Historical data, time-series analysis
- 3D model customization, changing colors programmatically
- Exporting data, generating reports
- Any feature not covered by the 5 tools above

Be concise and helpful. If unsure, it's better to say "not yet implemented" than to give incorrect information.

The map covers the greater Los Angeles area (approximately -118.7 to -118.15 longitude, 33.7 to 34.35 latitude).

Notable locations:
- LAX (Los Angeles International Airport): ~33.9416°N, 118.4085°W
- Long Beach Port: ~33.7545°N, 118.1933°W
- Downtown LA: ~34.0522°N, 118.2437°W"""

        # Build messages for Claude
        messages = []

        # Add conversation history
        for msg in conversation_history:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })

        # Add current user message
        messages.append({
            "role": "user",
            "content": user_message
        })

        # Call Claude API
        # Using Claude 3 Haiku for cost-effective responses
        response = anthropic_client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1024,
            system=system_prompt,
            tools=tools,
            messages=messages
        )

        # Process response
        response_data = {
            "text": "",
            "actions": [],
            "tool_calls": []
        }

        for block in response.content:
            if block.type == "text":
                response_data["text"] += block.text
            elif block.type == "tool_use":
                # Claude wants to use a tool
                response_data["actions"].append({
                    "tool": block.name,
                    "input": block.input,
                    "id": block.id
                })

        # If Claude used tools, we need to execute them and continue the conversation
        if response_data["actions"]:
            # For now, just return the tool calls to the frontend
            # The frontend will execute them and optionally send results back
            response_data["needs_tool_execution"] = True

        return jsonify(response_data)

    except Exception as e:
        print(f"Chat error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get infrastructure statistics"""
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # Get counts and details for each infrastructure type
        stats = {}

        # Airports stats
        cur.execute("""
            SELECT
                COUNT(*) as total,
                COUNT(DISTINCT class) as unique_classes,
                class,
                COUNT(*) as count
            FROM airports
            GROUP BY class
            ORDER BY count DESC
        """)
        airport_details = cur.fetchall()
        cur.execute("SELECT COUNT(*) as total FROM airports")
        stats['airports'] = {
            'total': cur.fetchone()['total'],
            'by_class': [dict(row) for row in airport_details]
        }

        # Ports stats
        cur.execute("""
            SELECT
                COUNT(*) as total,
                subtype,
                COUNT(*) as count
            FROM ports
            GROUP BY subtype
            ORDER BY count DESC
        """)
        port_details = cur.fetchall()
        cur.execute("SELECT COUNT(*) as total FROM ports")
        stats['ports'] = {
            'total': cur.fetchone()['total'],
            'by_subtype': [dict(row) for row in port_details]
        }

        # Warehouses stats
        cur.execute("""
            SELECT
                COUNT(*) as total,
                AVG(height) as avg_height,
                AVG(num_floors) as avg_floors
            FROM warehouses
        """)
        warehouse_stats = cur.fetchone()
        stats['warehouses'] = dict(warehouse_stats)

        cur.close()
        conn.close()

        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/route', methods=['POST'])
def calculate_route():
    """Calculate route between two points using TomTom API"""
    try:
        data = request.json
        start = data.get('start')  # {lat, lon}
        end = data.get('end')  # {lat, lon}

        if not start or not end:
            return jsonify({"error": "Start and end coordinates required"}), 400

        # Get TomTom API key
        tomtom_key = os.environ.get("TOMTOM_API_KEY")
        if not tomtom_key or tomtom_key == "your_tomtom_api_key_here":
            return jsonify({
                "error": "TomTom API key not configured",
                "message": "Please add your TomTom API key to the .env file"
            }), 503

        # Format coordinates for TomTom API
        locations = f"{start['lat']},{start['lon']}:{end['lat']},{end['lon']}"

        # Call TomTom Routing API
        tomtom_url = f"https://api.tomtom.com/routing/1/calculateRoute/{locations}/json"
        params = {
            'key': tomtom_key,
            'traffic': 'true',
            'travelMode': 'car'
        }

        response = requests.get(tomtom_url, params=params, timeout=10)
        response.raise_for_status()

        route_data = response.json()

        # Extract useful information
        if 'routes' in route_data and len(route_data['routes']) > 0:
            route = route_data['routes'][0]
            summary = route['summary']

            # Extract route geometry (coordinates)
            legs = route['legs']
            points = []
            for leg in legs:
                for point in leg['points']:
                    points.append([point['longitude'], point['latitude']])

            result = {
                'success': True,
                'route': {
                    'distance': summary['lengthInMeters'],
                    'distance_km': round(summary['lengthInMeters'] / 1000, 2),
                    'distance_miles': round(summary['lengthInMeters'] / 1609.34, 2),
                    'duration': summary['travelTimeInSeconds'],
                    'duration_minutes': round(summary['travelTimeInSeconds'] / 60, 1),
                    'traffic_delay': summary.get('trafficDelayInSeconds', 0),
                    'coordinates': points
                }
            }

            return jsonify(result)
        else:
            return jsonify({"error": "No route found"}), 404

    except requests.exceptions.RequestException as e:
        print(f"TomTom API error: {str(e)}")
        return jsonify({"error": f"Routing service error: {str(e)}"}), 502
    except Exception as e:
        print(f"Route calculation error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/find-nearest', methods=['POST'])
def find_nearest():
    """Find the nearest infrastructure feature to a given location"""
    try:
        data = request.json
        location = data.get('location')  # {lat, lon}
        infrastructure_type = data.get('infrastructure_type')  # 'airports', 'ports', or 'warehouses'

        if not location or not infrastructure_type:
            return jsonify({"error": "Location and infrastructure_type required"}), 400

        # Map infrastructure type to table name
        table_map = {
            'airports': 'airports',
            'ports': 'ports',
            'warehouses': 'warehouses'
        }

        table = table_map.get(infrastructure_type)
        if not table:
            return jsonify({"error": "Invalid infrastructure type"}), 400

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # Calculate distance using haversine formula approximation
        # Extract coordinates from geometry and calculate distance
        # Geometry structure: {coordinates: [[[lon, lat], [lon, lat], ...]]} for polygons
        query = f"""
            WITH coords AS (
                SELECT
                    id,
                    name,
                    subtype,
                    class,
                    geometry,
                    -- Extract first coordinate from the polygon
                    -- Structure: coordinates[0][0][0][0] = lon, coordinates[0][0][0][1] = lat
                    CAST((geometry->'coordinates'->0->0->0->>0) AS FLOAT) as lon,
                    CAST((geometry->'coordinates'->0->0->0->>1) AS FLOAT) as lat
                FROM {table}
                WHERE geometry->'coordinates'->0->0->0 IS NOT NULL
            )
            SELECT
                id,
                name,
                subtype,
                class,
                geometry,
                lat,
                lon,
                -- Haversine distance approximation in km
                6371 * acos(
                    LEAST(1.0, GREATEST(-1.0,
                        cos(radians(%s)) * cos(radians(lat)) *
                        cos(radians(lon) - radians(%s)) +
                        sin(radians(%s)) * sin(radians(lat))
                    ))
                ) as distance_km
            FROM coords
            WHERE lat IS NOT NULL AND lon IS NOT NULL
            ORDER BY distance_km
            LIMIT 1
        """

        cur.execute(query, (location['lat'], location['lon'], location['lat']))
        result = cur.fetchone()

        cur.close()
        conn.close()

        if result:
            return jsonify({
                'success': True,
                'feature': {
                    'id': result['id'],
                    'name': result['name'],
                    'subtype': result['subtype'],
                    'class': result['class'],
                    'coordinates': {
                        'lat': result['lat'],
                        'lon': result['lon']
                    },
                    'distance_km': round(result['distance_km'], 2),
                    'distance_miles': round(result['distance_km'] * 0.621371, 2)
                }
            })
        else:
            return jsonify({"error": "No features found"}), 404

    except Exception as e:
        print(f"Find nearest error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    print("Starting API server on http://localhost:5001")
    print("Endpoints:")
    print("  - GET  /api/airports")
    print("  - GET  /api/ports")
    print("  - GET  /api/warehouses")
    print("  - GET  /api/stats")
    print("  - POST /api/chat")
    print("  - POST /api/route")
    print("  - GET  /api/health")
    app.run(debug=True, port=5001)
