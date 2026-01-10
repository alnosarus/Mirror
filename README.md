# Mirror Project

3D infrastructure visualization for Los Angeles area using Overture Maps data, PostgreSQL, and DeckGL.

## Quick Start

### Install Dependencies

```bash
# Python dependencies
python3 -m pip install --user -r requirements.txt

# Frontend dependencies
cd app && npm install && cd ..
```

### Setup Database

```bash
python3 setup_postgres.py
```

### Run Application

```bash
# Option 1: Use the startup script
./start.sh

# Option 2: Manual start (two terminals)
# Terminal 1: API Server
python3 api_server.py

# Terminal 2: Frontend
cd app && npm run dev
```

### Stop Application

```bash
# Option 1: Use the stop script
./stop.sh

# Option 2: Manual stop
pkill -f "api_server.py|vite"
```

## Project Structure

```
Mirror/
├── README.md                 # This file
├── DEPENDENCIES.md           # Complete dependency list
├── POSTGRES_SETUP.md         # Database documentation
├── requirements.txt          # Python dependencies
├── start.sh                  # Startup script
├── stop.sh                   # Stop script
│
├── api_server.py             # Flask REST API (port 5001)
├── setup_postgres.py         # Database initialization
├── postgrestest.py           # Connection test
│
├── fetch_airports.sql        # DuckDB query for airports
├── fetch_ports.sql           # DuckDB query for ports
├── fetch_infrastructure.sql  # DuckDB query for infrastructure
│
└── app/                      # React frontend
    ├── package.json
    ├── vite.config.js
    ├── public/
    │   └── data/
    │       ├── la_airport_infrastructure.geojson
    │       └── la_port_infrastructure.geojson
    └── src/
        ├── Map.jsx           # Main map component
        ├── main.jsx
        └── index.css
```

## Features

- **3D Visualization**: WebGL-powered 3D rendering of infrastructure
- **PostgreSQL Backend**: Scalable database with 3,886 infrastructure features
  - 1,657 airports (terminals, helipads, runways, aprons)
  - 2,229 ports (piers, quays, marinas)
- **Real Data**: Sourced from Overture Maps (2025-12-17.0 release)
- **Interactive Map**: Tooltips, highlighting, and dynamic camera controls
- **Dark Theme**: Optimized color scheme for night viewing

## Tech Stack

### Frontend
- React 19.2.0
- DeckGL 9.2.5 (3D rendering)
- MapLibre GL 5.15.0 (base map)
- Vite 7.3.1 (build tool)

### Backend
- Python 3.9.6
- Flask 3.1.2 (REST API)
- PostgreSQL 17.5 (database)
- psycopg2-binary 2.9.9 (database driver)

### Data Pipeline
- DuckDB 1.4.3 (data extraction)
- Overture Maps (geospatial data source)

## API Endpoints

### GET /api/airports
Returns all airport infrastructure as GeoJSON FeatureCollection

**Example:**
```bash
curl http://localhost:5001/api/airports
```

**Response:**
```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "properties": {
        "id": "...",
        "name": "Los Angeles International Airport",
        "subtype": "airport",
        "class": "international_airport"
      },
      "geometry": {
        "type": "Polygon",
        "coordinates": [[...]]
      }
    }
  ]
}
```

### GET /api/ports
Returns all port infrastructure as GeoJSON FeatureCollection

### GET /api/health
Health check endpoint

**Response:**
```json
{
  "status": "ok"
}
```

## Database Schema

### airports
| Column   | Type         | Description                    |
|----------|--------------|--------------------------------|
| id       | VARCHAR(255) | Primary key (Overture Maps ID) |
| name     | VARCHAR(255) | Airport name                   |
| subtype  | VARCHAR(100) | Infrastructure subtype         |
| class    | VARCHAR(100) | Specific class type            |
| geometry | JSONB        | GeoJSON geometry               |

### ports
| Column   | Type         | Description                    |
|----------|--------------|--------------------------------|
| id       | VARCHAR(255) | Primary key (Overture Maps ID) |
| name     | VARCHAR(255) | Port/pier name                 |
| subtype  | VARCHAR(100) | Infrastructure subtype         |
| class    | VARCHAR(100) | Specific class type            |
| geometry | JSONB        | GeoJSON geometry               |

## Data Source

All infrastructure data is sourced from **Overture Maps Foundation**:
- Release: 2025-12-17.0
- Theme: base/infrastructure
- S3 Bucket: `s3://overturemaps-us-west-2/release/2025-12-17.0/`
- Area: Greater Los Angeles (bbox: -118.7 to -118.15 lon, 33.7 to 34.35 lat)

Data extraction performed using DuckDB with spatial extension.

## Development

### Adding New Data

1. Write DuckDB query in `fetch_*.sql`
2. Run query: `duckdb < fetch_*.sql`
3. Update `setup_postgres.py` to load new GeoJSON
4. Add new table schema
5. Create API endpoint in `api_server.py`
6. Update Map.jsx to render new layer

### Database Management

```bash
# Connect to database
psql -U postgres -d mirror

# View tables
\dt

# Query airports
SELECT name, class FROM airports LIMIT 10;

# Drop and recreate
python3 setup_postgres.py
```

## Troubleshooting

### PostgreSQL not running
```bash
brew services start postgresql@17
```

### Port conflicts
- API server uses port 5001
- Frontend uses port 5174 (or next available)
- Check terminal output for actual ports

### Module not found errors
Make sure you're using system Python (`python3`), not Homebrew Python:
```bash
python3 -m pip install --user -r requirements.txt
```

### Database connection errors
Check database exists and credentials in `api_server.py`:
```python
DB_PARAMS = {
    "dbname": "mirror",
    "user": "postgres",
    "password": "1234!",
    "host": "localhost",
    "port": "5432"
}
```

## Documentation

- [DEPENDENCIES.md](DEPENDENCIES.md) - Complete dependency list and installation
- [POSTGRES_SETUP.md](POSTGRES_SETUP.md) - Database setup guide

## License

Data from Overture Maps Foundation (licensed under ODbL)
