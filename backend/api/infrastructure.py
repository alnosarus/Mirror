"""
Infrastructure API endpoints
"""
from fastapi import APIRouter, HTTPException
from database.queries import get_infrastructure, get_supply_chain_connections, get_connections_geojson

router = APIRouter(prefix="/api/infrastructure", tags=["infrastructure"])

@router.get("/")
async def list_infrastructure():
    """Get all infrastructure"""
    try:
        infrastructure = get_infrastructure()
        return {"infrastructure": [dict(i) for i in infrastructure]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/connections")
async def list_connections():
    """Get supply chain connections"""
    try:
        connections = get_supply_chain_connections()
        return {"connections": [dict(c) for c in connections]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/connections/geojson")
async def connections_geojson():
    """Get supply chain connections in GeoJSON format for mapping"""
    try:
        geojson = get_connections_geojson()
        return geojson
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
