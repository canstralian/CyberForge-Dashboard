from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
import logging
from typing import List

from src.api.database import get_db
from src.api.auth import get_current_user
from src.api.routers import threats_router, indicators_router, auth_router, admin_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("app.log")
    ]
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="CyberForge OSINT API",
    description="API for Dark Web OSINT platform",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers for different endpoints
app.include_router(auth_router.router, prefix="/api/v1")
app.include_router(
    threats_router.router, 
    prefix="/api/v1/threats",
    tags=["threats"],
    dependencies=[Depends(get_current_user)]
)
app.include_router(
    indicators_router.router, 
    prefix="/api/v1/indicators",
    tags=["indicators"],
    dependencies=[Depends(get_current_user)]
)
app.include_router(
    admin_router.router, 
    prefix="/api/v1/admin",
    tags=["admin"],
    dependencies=[Depends(get_current_user)]
)

@app.get("/api/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "healthy", "version": "1.0.0"}

@app.on_event("startup")
async def startup_event():
    """Event handler for application startup."""
    logger.info("Starting the CyberForge OSINT API")
    # Add any startup tasks here (database connection, cache warming, etc.)

@app.on_event("shutdown")
async def shutdown_event():
    """Event handler for application shutdown."""
    logger.info("Shutting down the CyberForge OSINT API")
    # Add any cleanup tasks here (close connections, save state, etc.)