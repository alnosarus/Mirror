# Dependencies and Installation Guide

This document lists all required dependencies and installation steps for the Mirror Project.

## System Requirements

- **Node.js**: v18+ (for frontend)
- **Python**: 3.9+ (for backend)
- **PostgreSQL**: 17.5+ (for database)
- **DuckDB**: Latest (for data extraction)
- **Homebrew**: (macOS package manager)

---

## Backend Dependencies (Python)

### Required Python Packages

Install all Python dependencies:

```bash
python3 -m pip install --user psycopg2-binary flask flask-cors
```

#### Individual Packages:

1. **psycopg2-binary** (2.9.9)
   - PostgreSQL database adapter
   - Used for: Database connections and queries

2. **flask** (3.1.2)
   - Web framework for API server
   - Used for: REST API endpoints

3. **flask-cors** (6.0.2)
   - Cross-Origin Resource Sharing support
   - Used for: Allowing frontend to access API

### Python Standard Library (No Installation Required)

- `json` - JSON parsing
- `psycopg2.extras` - PostgreSQL dictionary cursors
- `psycopg2.extensions` - PostgreSQL isolation levels

---

## Frontend Dependencies (Node.js/npm)

### Install Frontend Dependencies

Navigate to the app directory and install:

```bash
cd app
npm install
```

### Package.json Dependencies

```json
{
  "dependencies": {
    "react": "^19.2.0",
    "react-dom": "^19.2.0"
  },
  "devDependencies": {
    "@eslint/js": "^10.1.0",
    "@types/react": "^19.0.6",
    "@types/react-dom": "^19.0.2",
    "@vitejs/plugin-react": "^4.4.0",
    "eslint": "^9.20.0",
    "eslint-plugin-react": "^7.37.3",
    "eslint-plugin-react-hooks": "^5.1.0",
    "eslint-plugin-react-refresh": "^0.4.17",
    "globals": "^15.14.0",
    "vite": "^7.3.1"
  }
}
```

### Additional npm Packages (Already in package.json)

1. **@deck.gl/core** (9.2.5)
   - WebGL-powered visualization framework
   - Used for: 3D map rendering

2. **@deck.gl/react** (9.2.5)
   - React bindings for Deck.gl
   - Used for: React integration

3. **@deck.gl/layers** (9.2.5)
   - Layer components for Deck.gl
   - Used for: GeoJsonLayer, PolygonLayer

4. **react-map-gl** (8.1.0)
   - React wrapper for MapLibre GL
   - Used for: Map component

5. **maplibre-gl** (5.15.0)
   - Open-source map rendering library
   - Used for: Base map tiles and rendering

---

## Database Setup

### Install PostgreSQL

```bash
brew install postgresql@17
brew services start postgresql@17
```

### Create Database

```bash
createdb mirror
```

### Initialize Database Schema and Load Data

```bash
python3 setup_postgres.py
```

This will:
- Create `airports` and `ports` tables
- Load 1,657 airport features
- Load 2,229 port features
- Create indices for performance

---

## Data Extraction Tools

### Install DuckDB

```bash
brew install duckdb
```

### DuckDB Extensions

DuckDB will automatically install these when running the SQL queries:

- **spatial** - Spatial data support and GeoJSON export

### Run Data Extraction (Optional - already completed)

```bash
# Extract airports
duckdb < fetch_airports.sql

# Extract ports
duckdb < fetch_ports.sql

# Extract infrastructure polygons
duckdb < fetch_infrastructure.sql
```

---

## Complete Installation Steps

### 1. Install System Dependencies

```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install PostgreSQL
brew install postgresql@17
brew services start postgresql@17

# Install DuckDB (for data extraction)
brew install duckdb
```

### 2. Install Python Dependencies

```bash
python3 -m pip install --user psycopg2-binary flask flask-cors
```

### 3. Install Frontend Dependencies

```bash
cd app
npm install
```

### 4. Setup Database

```bash
# Create database (if not exists)
createdb mirror

# Load data into PostgreSQL
python3 setup_postgres.py
```

---

## Running the Application

### Start Backend API Server

```bash
python3 api_server.py
```

Runs on: http://localhost:5001

### Start Frontend Dev Server

```bash
cd app
npm run dev
```

Runs on: http://localhost:5174

### Open in Browser

Navigate to: http://localhost:5174

---

## Stopping the Application

### Stop API Server

```bash
pkill -f api_server.py
```

### Stop Frontend Server

```bash
pkill -f vite
```

### Stop Both

```bash
pkill -f "api_server.py|vite"
```

---

## File Structure

```
Mirror/
├── api_server.py              # Flask API server
├── setup_postgres.py          # Database setup script
├── postgrestest.py           # DB connection test
├── fetch_airports.sql        # DuckDB query for airports
├── fetch_ports.sql           # DuckDB query for ports
├── fetch_infrastructure.sql  # DuckDB query for infrastructure
├── DEPENDENCIES.md           # This file
├── POSTGRES_SETUP.md         # PostgreSQL documentation
└── app/
    ├── package.json          # Node.js dependencies
    ├── vite.config.js        # Vite configuration
    ├── public/
    │   └── data/
    │       ├── la_airport_infrastructure.geojson
    │       └── la_port_infrastructure.geojson
    └── src/
        ├── Map.jsx           # Main map component
        ├── main.jsx          # React entry point
        └── index.css         # Styles
```

---

## Troubleshooting

### PostgreSQL Connection Issues

If you get connection errors, check PostgreSQL is running:

```bash
brew services list | grep postgresql
```

Restart if needed:

```bash
brew services restart postgresql@17
```

### Python Module Not Found

Make sure you're using the correct Python:

```bash
# Use system Python (has psycopg2)
python3 script.py

# NOT Homebrew Python
/opt/homebrew/bin/python3 script.py  # Won't work
```

### Port Already in Use

If port 5001 or 5174 is busy, Vite will automatically use the next available port. Check the terminal output for the actual port.

---

## Version Information

- **Python**: 3.9.6
- **PostgreSQL**: 17.5
- **Node.js**: Check with `node --version`
- **npm**: Check with `npm --version`
- **DuckDB**: 1.4.3
- **Overture Maps Data**: 2025-12-17.0 release
