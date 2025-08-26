"""
Ghost Protocol API Routes
"""

from fastapi import APIRouter
from .beacons import router as beacons_router
from .listeners import router as listeners_router
from .modules import router as modules_router
from .operations import router as operations_router
from .auth import router as auth_router


def setup_routes() -> APIRouter:
    """Setup all API routes"""
    api_router = APIRouter(prefix="/api/v1")
    
    api_router.include_router(auth_router, prefix="/auth", tags=["authentication"])
    api_router.include_router(beacons_router, prefix="/beacons", tags=["beacons"])
    api_router.include_router(listeners_router, prefix="/listeners", tags=["listeners"])
    api_router.include_router(modules_router, prefix="/modules", tags=["modules"])
    api_router.include_router(operations_router, prefix="/operations", tags=["operations"])
    
    return api_router
