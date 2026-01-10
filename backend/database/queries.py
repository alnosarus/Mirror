"""
Database query functions
"""
from database.connection import get_db_connection
import json

def get_all_facilities():
    """Get all facilities with their locations"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, name, type, latitude, longitude, capacity, properties
            FROM facilities
            ORDER BY id
        """)
        facilities = cursor.fetchall()
        cursor.close()
        return facilities

def get_facilities_geojson():
    """Get facilities in GeoJSON format for deck.gl"""
    facilities = get_all_facilities()

    features = []
    for facility in facilities:
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [float(facility['longitude']), float(facility['latitude'])]
            },
            "properties": {
                "id": facility['id'],
                "name": facility['name'],
                "type": facility['type'],
                "capacity": facility['capacity'],
                **(facility['properties'] or {})
            }
        }
        features.append(feature)

    return {
        "type": "FeatureCollection",
        "features": features
    }

def get_infrastructure():
    """Get all infrastructure"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, name, type, latitude, longitude, geojson, properties
            FROM infrastructure
            ORDER BY type, id
        """)
        infrastructure = cursor.fetchall()
        cursor.close()
        return infrastructure

def get_supply_chain_connections():
    """Get supply chain connections with facility details"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                sc.id,
                sc.connection_type,
                sc.flow_volume,
                f1.name as from_facility_name,
                f1.latitude as from_latitude,
                f1.longitude as from_longitude,
                f2.name as to_facility_name,
                f2.latitude as to_latitude,
                f2.longitude as to_longitude
            FROM supply_chain_connections sc
            JOIN facilities f1 ON sc.from_facility_id = f1.id
            JOIN facilities f2 ON sc.to_facility_id = f2.id
            ORDER BY sc.id
        """)
        connections = cursor.fetchall()
        cursor.close()
        return connections

def get_connections_geojson():
    """Get supply chain connections in GeoJSON format for deck.gl ArcLayer"""
    connections = get_supply_chain_connections()

    features = []
    for conn in connections:
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "LineString",
                "coordinates": [
                    [float(conn['from_longitude']), float(conn['from_latitude'])],
                    [float(conn['to_longitude']), float(conn['to_latitude'])]
                ]
            },
            "properties": {
                "id": conn['id'],
                "from": conn['from_facility_name'],
                "to": conn['to_facility_name'],
                "type": conn['connection_type'],
                "flow_volume": conn['flow_volume']
            }
        }
        features.append(feature)

    return {
        "type": "FeatureCollection",
        "features": features
    }

def get_simulation(simulation_id):
    """Get simulation by ID"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, scenario_name, description, start_date, duration_days,
                   total_impact, status, created_at, completed_at
            FROM simulations
            WHERE id = %s
        """, (simulation_id,))
        simulation = cursor.fetchone()
        cursor.close()
        return simulation

def get_simulation_timeline(simulation_id):
    """Get simulation timeline with facility states"""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Get timeline events
        cursor.execute("""
            SELECT day, timestamp, events
            FROM simulation_timeline
            WHERE simulation_id = %s
            ORDER BY day
        """, (simulation_id,))
        timeline = cursor.fetchall()

        # Get facility states for each day
        cursor.execute("""
            SELECT
                fs.day,
                fs.status,
                fs.impact_cost,
                f.id as facility_id,
                f.name as facility_name,
                f.latitude,
                f.longitude,
                f.type as facility_type
            FROM facility_states fs
            JOIN facilities f ON fs.facility_id = f.id
            WHERE fs.simulation_id = %s
            ORDER BY fs.day, f.id
        """, (simulation_id,))
        facility_states = cursor.fetchall()

        cursor.close()

        # Group facility states by day
        states_by_day = {}
        for state in facility_states:
            day = state['day']
            if day not in states_by_day:
                states_by_day[day] = []
            states_by_day[day].append(dict(state))

        # Combine timeline with facility states
        result = []
        for timeline_entry in timeline:
            day = timeline_entry['day']
            result.append({
                'day': day,
                'timestamp': timeline_entry['timestamp'].isoformat() if timeline_entry['timestamp'] else None,
                'events': timeline_entry['events'],
                'facility_states': states_by_day.get(day, [])
            })

        return result

def get_all_simulations():
    """Get all simulations"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, scenario_name, description, duration_days,
                   total_impact, status, created_at
            FROM simulations
            ORDER BY created_at DESC
        """)
        simulations = cursor.fetchall()
        cursor.close()
        return simulations
