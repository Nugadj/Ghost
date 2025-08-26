"""
Ghost Protocol Listeners API Routes
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from ..auth import AuthService
from ...database.models import User

router = APIRouter()


class CreateListenerRequest(BaseModel):
    """Create listener request model"""
    name: str
    type: str = "http"
    host: str = "0.0.0.0"
    port: int
    config: Dict[str, Any] = {}


class ListenerResponse(BaseModel):
    """Listener response model"""
    listener_id: str
    name: str
    type: str
    host: str
    port: int
    status: str
    config: Dict[str, Any]


@router.post("/", response_model=ListenerResponse)
async def create_listener(
    request: CreateListenerRequest,
    current_user: User = Depends(AuthService.get_current_user)
):
    """Create a new listener"""
    # This would integrate with listener manager
    return ListenerResponse(
        listener_id="mock-listener-id",
        name=request.name,
        type=request.type,
        host=request.host,
        port=request.port,
        status="stopped",
        config=request.config
    )


@router.get("/", response_model=List[ListenerResponse])
async def list_listeners(
    current_user: User = Depends(AuthService.get_current_user)
):
    """List all listeners"""
    # This would integrate with listener manager
    return []


@router.post("/{listener_id}/start")
async def start_listener(
    listener_id: str,
    current_user: User = Depends(AuthService.get_current_user)
):
    """Start a listener"""
    # This would integrate with listener manager
    return {"success": True}


@router.post("/{listener_id}/stop")
async def stop_listener(
    listener_id: str,
    current_user: User = Depends(AuthService.get_current_user)
):
    """Stop a listener"""
    # This would integrate with listener manager
    return {"success": True}


@router.delete("/{listener_id}")
async def delete_listener(
    listener_id: str,
    current_user: User = Depends(AuthService.get_current_user)
):
    """Delete a listener"""
    # This would integrate with listener manager
    return {"success": True}
