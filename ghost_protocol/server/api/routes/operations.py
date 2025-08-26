"""
Ghost Protocol Operations API Routes
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from datetime import datetime

from ..auth import AuthService
from ...database.models import User

router = APIRouter()


class CreateOperationRequest(BaseModel):
    """Create operation request model"""
    name: str
    description: Optional[str] = ""


class OperationResponse(BaseModel):
    """Operation response model"""
    operation_id: str
    name: str
    description: str
    start_time: datetime
    end_time: Optional[datetime]
    status: str
    owner_id: str


@router.post("/", response_model=OperationResponse)
async def create_operation(
    request: CreateOperationRequest,
    current_user: User = Depends(AuthService.get_current_user)
):
    """Create a new operation"""
    # This would integrate with the server core
    operation_data = {
        "name": request.name,
        "description": request.description,
        "owner_id": str(current_user.user_id)
    }
    
    # Mock response for now
    return OperationResponse(
        operation_id="mock-operation-id",
        name=request.name,
        description=request.description,
        start_time=datetime.utcnow(),
        end_time=None,
        status="active",
        owner_id=str(current_user.user_id)
    )


@router.get("/", response_model=List[OperationResponse])
async def list_operations(
    current_user: User = Depends(AuthService.get_current_user)
):
    """List operations for current user"""
    # This would integrate with the server core
    return []


@router.get("/{operation_id}", response_model=OperationResponse)
async def get_operation(
    operation_id: str,
    current_user: User = Depends(AuthService.get_current_user)
):
    """Get operation details"""
    # This would integrate with the server core
    raise HTTPException(status_code=404, detail="Operation not found")


@router.delete("/{operation_id}")
async def delete_operation(
    operation_id: str,
    current_user: User = Depends(AuthService.get_current_user)
):
    """Delete an operation"""
    # This would integrate with the server core
    return {"success": True}
