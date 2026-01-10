"""
Simulations API endpoints
"""
from fastapi import APIRouter, HTTPException
from database.queries import get_all_simulations, get_simulation, get_simulation_timeline

router = APIRouter(prefix="/api/simulations", tags=["simulations"])

@router.get("/")
async def list_simulations():
    """Get all simulations"""
    try:
        simulations = get_all_simulations()
        return {"simulations": [dict(s) for s in simulations]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{simulation_id}")
async def get_simulation_by_id(simulation_id: int):
    """Get simulation by ID"""
    try:
        simulation = get_simulation(simulation_id)
        if not simulation:
            raise HTTPException(status_code=404, detail="Simulation not found")
        return dict(simulation)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{simulation_id}/timeline")
async def get_simulation_timeline_data(simulation_id: int):
    """Get simulation timeline with facility states for animation"""
    try:
        # Check if simulation exists
        simulation = get_simulation(simulation_id)
        if not simulation:
            raise HTTPException(status_code=404, detail="Simulation not found")

        timeline = get_simulation_timeline(simulation_id)
        return {
            "simulation_id": simulation_id,
            "timeline": timeline
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
