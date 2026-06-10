from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.common import success_response
from app.middleware.auth import get_current_user
from app.services.user import user_service
from app.models import User

router = APIRouter()


@router.get("/me/permissions")
async def get_my_permissions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取当前用户权限"""
    permissions = user_service.get_user_permissions(db, current_user.id)
    return success_response(data=permissions)


@router.get("/me/roles")
async def get_my_roles(
    current_user: User = Depends(get_current_user),
):
    """获取当前用户角色"""
    roles = [{"id": r.id, "name": r.name, "description": r.description} for r in current_user.roles]
    return success_response(data=roles)
