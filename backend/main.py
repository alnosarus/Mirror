"""
Mirror API - FastAPI Backend
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import facilities, infrastructure, simulations

app = FastAPI(
    title="Mirror API",
    description="Infrastructure disruption simulation API",
    version="0.1.0"
)

# CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(facilities.router)
app.include_router(infrastructure.router)
app.include_router(simulations.router)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Mirror API",
        "version": "0.1.0",
        "endpoints": {
            "facilities": "/api/facilities",
            "infrastructure": "/api/infrastructure",
            "simulations": "/api/simulations",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
