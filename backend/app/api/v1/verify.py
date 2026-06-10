from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.common import success_response, error_response
from app.schemas.permission import PermissionVerifyRequest
from app.services.permission import permission_service
from app.services.user import user_service
from app.models import User

router = APIRouter()


@router.post("/verify")
async def verify_permission(
    data: PermissionVerifyRequest,
    db: Session = Depends(get_db),
):
    """验证用户权限(对外API，供其他系统/Agent调用)"""
    result = permission_service.verify_permission(db, data.user_id, data.type, data.target_name)
    return success_response(data=result)


@router.get("/users/{user_id}/tools")
async def get_user_tools(
    user_id: int,
    db: Session = Depends(get_db),
):
    """获取用户可用工具列表(对外API)"""
    permissions = user_service.get_user_permissions(db, user_id)
    return success_response(data=permissions)


@router.get("/users/{user_id}/skills")
async def get_user_skills(
    user_id: int,
    db: Session = Depends(get_db),
):
    """获取用户可用技能列�?对外API)"""
    permissions = user_service.get_user_permissions(db, user_id)
    return success_response(data={"skills": permissions["skills"]})
