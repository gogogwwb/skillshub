from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.common import success_response, error_response
from app.schemas.user import UserRoleUpdate, UserStatusUpdate
from app.middleware.auth import require_admin
from app.services.user import user_service
from app.services.audit import audit_service
from app.models import User

router = APIRouter()


@router.get("")
async def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: str = Query(None),
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Get user list"""
    users, total = user_service.get_user_list(db, page, page_size, keyword)
    result = []
    for u in users:
        result.append({
            "id": u.id,
            "feishu_id": u.feishu_id,
            "name": u.name,
            "email": u.email,
            "avatar": u.avatar,
            "department_id": u.department_id,
            "department_name": u.department.name if u.department else None,
            "status": u.status,
            "is_admin": u.is_admin,
            "roles": [{"id": r.id, "name": r.name} for r in u.roles],
            "created_at": u.created_at.isoformat() if u.created_at else None,
        })
    return success_response(data={"items": result, "total": total, "page": page, "page_size": page_size})


@router.get("/{user_id}")
async def get_user(
    user_id: int,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Get user detail"""
    user = user_service.get_user_detail(db, user_id)
    if not user:
        return error_response(message="User not found")
    return success_response(data={
        "id": user.id,
        "feishu_id": user.feishu_id,
        "name": user.name,
        "email": user.email,
        "avatar": user.avatar,
        "department_id": user.department_id,
        "department_name": user.department.name if user.department else None,
        "status": user.status,
        "is_admin": user.is_admin,
        "roles": [{"id": r.id, "name": r.name, "description": r.description} for r in user.roles],
        "created_at": user.created_at.isoformat() if user.created_at else None,
    })


@router.put("/{user_id}/roles")
async def update_user_roles(
    user_id: int,
    data: UserRoleUpdate,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Assign roles to user"""
    try:
        user = user_service.update_user_roles(db, user_id, data.role_ids)
        audit_service.log(db, admin.id, "update", "user", user_id, {"action": "assign_roles", "role_ids": data.role_ids})
        return success_response(message="Roles updated")
    except ValueError as e:
        return error_response(message=str(e))


@router.put("/{user_id}/status")
async def update_user_status(
    user_id: int,
    data: UserStatusUpdate,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Update user status"""
    try:
        user = user_service.update_user_status(db, user_id, data.status)
        audit_service.log(db, admin.id, "update", "user", user_id, {"action": "change_status", "status": data.status})
        return success_response(message="Status updated")
    except ValueError as e:
        return error_response(message=str(e))
