"""
Ghost Protocol Authentication API Routes
"""

from fastapi import APIRouter, Depends, HTTPException
from ..auth import AuthService, LoginRequest, LoginResponse
from ...database.models import User

router = APIRouter()
auth_service = AuthService()


@router.post("/login", response_model=LoginResponse)
async def login(login_request: LoginRequest):
    """Login endpoint"""
    return await auth_service.login(login_request)


@router.get("/me")
async def get_current_user_info(current_user: User = Depends(auth_service.get_current_user)):
    """Get current user information"""
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "role": current_user.role,
        "is_active": current_user.is_active
    }


@router.post("/logout")
async def logout(current_user: User = Depends(auth_service.get_current_user)):
    """Logout endpoint (token invalidation would be handled client-side)"""
    return {"message": "Successfully logged out"}
