# PostgreSQL Setup Guide

This project now uses PostgreSQL to store and serve infrastructure data (airports and ports) instead of static GeoJSON files.

## Database Structure

### Tables

**airports**
- `id` (VARCHAR, PRIMARY KEY): Unique identifier from Overture Maps
- `name` (VARCHAR): Name of the airport
- `subtype` (VARCHAR): Infrastructure subtype (e.g., "airport")
- `class` (VARCHAR): Specific class (e.g., "international_airport", "helipad")
- `geometry` (JSONB): GeoJSON geometry (Polygon or Point)

**ports**
- `id` (VARCHAR, PRIMARY KEY): Unique identifier from Overture Maps
- `name` (VARCHAR): Name of the port/pier
- `subtype` (VARCHAR): Infrastructure subtype (e.g., "pier", "quay")
- `class` (VARCHAR): Specific class
- `geometry` (JSONB): GeoJSON geometry (Polygon, LineString, or Point)

## Data Statistics

- **Airports**: 1,657 features loaded
- **Ports**: 2,229 features loaded

All data sourced from Overture Maps (2025-12-17.0 release)

## Setup Instructions

### 1. Database Setup

Run the setup script to create tables and load data:

```bash
python3 setup_postgres.py
```

This will:
- Create the `airports` and `ports` tables
- Load data from GeoJSON files into PostgreSQL
- Create indices for better query performance

### 2. Start the API Server

Run the Flask API server:

```bash
python3 api_server.py
```

The API will be available at `http://localhost:5001`

### 3. Start the Frontend

```bash
cd app
npm run dev
```

The map will now fetch data from PostgreSQL via the API.

## API Endpoints

### GET /api/airports
Returns all airport infrastructure as GeoJSON FeatureCollection

Example:
```bash
curl http://localhost:5001/api/airports
```

### GET /api/ports
Returns all port infrastructure as GeoJSON FeatureCollection

Example:
```bash
curl http://localhost:5001/api/ports
```

### GET /api/health
Health check endpoint

Example:
```bash
curl http://localhost:5001/api/health
# Returns: {"status": "ok"}
```

## Files

- `setup_postgres.py` - Database setup and data loading script
- `api_server.py` - Flask API server for serving data
- `postgrestest.py` - Simple connection test script
- `app/src/Map.jsx` - Frontend map component (updated to use PostgreSQL API)

## Connection Details

- **Database**: mirror
- **User**: postgres
- **Host**: localhost
- **Port**: 5432

## Tech Stack

- **Database**: PostgreSQL 17.5
- **API**: Flask 3.1.2 with Flask-CORS
- **Python**: 3.9.6
- **PostgreSQL Driver**: psycopg2-binary

## Why PostgreSQL?

Benefits over static GeoJSON files:
1. **Dynamic queries**: Can filter, search, and aggregate data
2. **Scalability**: Better performance with large datasets
3. **Updates**: Easy to add/update/delete features
4. **Relational**: Can add related tables (e.g., flight data, port statistics)
5. **Standard**: Industry-standard database with extensive tooling
