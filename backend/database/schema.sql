-- Mirror Database Schema
-- Initial version without PostGIS (can be upgraded later)

-- Infrastructure table (roads, power lines, ports, water systems)
CREATE TABLE IF NOT EXISTS infrastructure (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(100) NOT NULL, -- 'road', 'port', 'power_line', 'water_system'
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    geojson JSONB, -- Store full GeoJSON geometry
    properties JSONB, -- Additional properties (capacity, etc.)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index on type for faster filtering
CREATE INDEX IF NOT EXISTS infrastructure_type_idx ON infrastructure(type);

-- Create index on lat/lng for spatial queries (basic)
CREATE INDEX IF NOT EXISTS infrastructure_location_idx ON infrastructure(latitude, longitude);

-- Facilities table (customer operations, ports, warehouses, factories)
CREATE TABLE IF NOT EXISTS facilities (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(100) NOT NULL, -- 'port', 'warehouse', 'factory', 'distribution_center'
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    capacity INTEGER,
    properties JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX IF NOT EXISTS facilities_type_idx ON facilities(type);
CREATE INDEX IF NOT EXISTS facilities_location_idx ON facilities(latitude, longitude);

-- Simulations table (store simulation metadata)
CREATE TABLE IF NOT EXISTS simulations (
    id SERIAL PRIMARY KEY,
    scenario_name VARCHAR(255) NOT NULL,
    description TEXT,
    start_date TIMESTAMP,
    duration_days INTEGER,
    total_impact BIGINT, -- Economic impact in dollars
    status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'running', 'completed', 'failed'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

-- Simulation timeline (time-series data for animation)
CREATE TABLE IF NOT EXISTS simulation_timeline (
    id SERIAL PRIMARY KEY,
    simulation_id INTEGER REFERENCES simulations(id) ON DELETE CASCADE,
    day INTEGER NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    events JSONB, -- Array of events that occurred on this day
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS simulation_timeline_sim_idx ON simulation_timeline(simulation_id);
CREATE INDEX IF NOT EXISTS simulation_timeline_day_idx ON simulation_timeline(simulation_id, day);

-- Facility states (track facility status over time in simulation)
CREATE TABLE IF NOT EXISTS facility_states (
    id SERIAL PRIMARY KEY,
    simulation_id INTEGER REFERENCES simulations(id) ON DELETE CASCADE,
    facility_id INTEGER REFERENCES facilities(id) ON DELETE CASCADE,
    day INTEGER NOT NULL,
    status VARCHAR(50) NOT NULL, -- 'operational', 'warning', 'degraded', 'offline'
    impact_cost BIGINT DEFAULT 0,
    properties JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS facility_states_sim_idx ON facility_states(simulation_id);
CREATE INDEX IF NOT EXISTS facility_states_facility_idx ON facility_states(facility_id);
CREATE INDEX IF NOT EXISTS facility_states_day_idx ON facility_states(simulation_id, day);

-- Supply chain connections (arcs between facilities)
CREATE TABLE IF NOT EXISTS supply_chain_connections (
    id SERIAL PRIMARY KEY,
    from_facility_id INTEGER REFERENCES facilities(id) ON DELETE CASCADE,
    to_facility_id INTEGER REFERENCES facilities(id) ON DELETE CASCADE,
    connection_type VARCHAR(100), -- 'supplier', 'customer', 'transport'
    flow_volume INTEGER,
    properties JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS supply_chain_from_idx ON supply_chain_connections(from_facility_id);
CREATE INDEX IF NOT EXISTS supply_chain_to_idx ON supply_chain_connections(to_facility_id);

-- Connection states during simulation
CREATE TABLE IF NOT EXISTS connection_states (
    id SERIAL PRIMARY KEY,
    simulation_id INTEGER REFERENCES simulations(id) ON DELETE CASCADE,
    connection_id INTEGER REFERENCES supply_chain_connections(id) ON DELETE CASCADE,
    day INTEGER NOT NULL,
    status VARCHAR(50) NOT NULL, -- 'active', 'disrupted', 'severed'
    flow_percentage INTEGER DEFAULT 100,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS connection_states_sim_idx ON connection_states(simulation_id);
CREATE INDEX IF NOT EXISTS connection_states_day_idx ON connection_states(simulation_id, day);

-- Insert sample data for Los Angeles
-- Port of LA
INSERT INTO facilities (name, type, latitude, longitude, capacity, properties)
VALUES (
    'Port of Los Angeles',
    'port',
    33.7428,
    -118.2725,
    9000000,
    '{"description": "Largest port in the Western Hemisphere", "teus_per_year": 9000000}'
) ON CONFLICT DO NOTHING;

-- Port of Long Beach
INSERT INTO facilities (name, type, latitude, longitude, capacity, properties)
VALUES (
    'Port of Long Beach',
    'port',
    33.7550,
    -118.1893,
    8000000,
    '{"description": "Second busiest port in the US", "teus_per_year": 8000000}'
) ON CONFLICT DO NOTHING;

-- Sample warehouse
INSERT INTO facilities (name, type, latitude, longitude, capacity, properties)
VALUES (
    'LA Distribution Center',
    'warehouse',
    34.0522,
    -118.2437,
    500000,
    '{"description": "Major distribution center", "square_feet": 500000}'
) ON CONFLICT DO NOTHING;

-- Sample factory
INSERT INTO facilities (name, type, latitude, longitude, capacity, properties)
VALUES (
    'Manufacturing Plant Alpha',
    'factory',
    34.1478,
    -118.1445,
    100000,
    '{"description": "Electronics manufacturing", "units_per_day": 10000}'
) ON CONFLICT DO NOTHING;

-- Create supply chain connections
INSERT INTO supply_chain_connections (from_facility_id, to_facility_id, connection_type, flow_volume)
SELECT f1.id, f2.id, 'supplier', 5000
FROM facilities f1, facilities f2
WHERE f1.name = 'Port of Los Angeles' AND f2.name = 'LA Distribution Center'
ON CONFLICT DO NOTHING;

INSERT INTO supply_chain_connections (from_facility_id, to_facility_id, connection_type, flow_volume)
SELECT f1.id, f2.id, 'customer', 3000
FROM facilities f1, facilities f2
WHERE f1.name = 'LA Distribution Center' AND f2.name = 'Manufacturing Plant Alpha'
ON CONFLICT DO NOTHING;

-- Create a sample simulation
INSERT INTO simulations (scenario_name, description, start_date, duration_days, total_impact, status)
VALUES (
    'Port of LA Closure - 2 Weeks',
    'Simulation of Port of LA closing for 2 weeks due to labor strike',
    NOW(),
    14,
    8000000000,
    'completed'
) ON CONFLICT DO NOTHING;
