"""
Facilities API endpoints
"""
from fastapi import APIRouter, HTTPException
from database.queries import get_all_facilities, get_facilities_geojson

router = APIRouter(prefix="/api/facilities", tags=["facilities"])

@router.get("/")
async def list_facilities():
    """Get all facilities"""
    try:
        facilities = get_all_facilities()
        return {"facilities": [dict(f) for f in facilities]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/geojson")
async def facilities_geojson():
    """Get facilities in GeoJSON format for mapping"""
    try:
        geojson = get_facilities_geojson()
        return geojson
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
