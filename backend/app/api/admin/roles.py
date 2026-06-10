from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.common import success_response, error_response
from app.schemas.role import RoleCreate, RoleUpdate, RoleSkillAssign, RoleToolAssign
from app.middleware.auth import require_admin
from app.services.role import role_service
from app.services.audit import audit_service
from app.models import User

router = APIRouter()


@router.get("")
async def list_roles(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Get role list"""
    roles = role_service.get_role_list(db)
    result = []
    for r in roles:
        result.append({
            "id": r.id,
            "name": r.name,
            "description": r.description,
            "skills": [{"id": s.id, "name": s.name} for s in r.skills],
            "tools": [{"id": t.id, "name": t.name} for t in r.tools],
            "user_count": len(r.users) if r.users else 0,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        })
    return success_response(data=result)


@router.post("")
async def create_role(
    data: RoleCreate,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Create role"""
    try:
        role = role_service.create_role(db, data)
        audit_service.log(db, admin.id, "create", "role", role.id, {"name": data.name})
        return success_response(data={"id": role.id, "name": role.name})
    except Exception as e:
        return error_response(message=str(e))


@router.put("/{role_id}")
async def update_role(
    role_id: int,
    data: RoleUpdate,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Update role"""
    try:
        role = role_service.update_role(db, role_id, data)
        audit_service.log(db, admin.id, "update", "role", role_id, data.model_dump(exclude_none=True))
        return success_response(message="Role updated")
    except ValueError as e:
        return error_response(message=str(e))


@router.delete("/{role_id}")
async def delete_role(
    role_id: int,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Delete role"""
    try:
        role_service.delete_role(db, role_id)
        audit_service.log(db, admin.id, "delete", "role", role_id)
        return success_response(message="Role deleted")
    except ValueError as e:
        return error_response(message=str(e))


@router.put("/{role_id}/skills")
async def assign_skills(
    role_id: int,
    data: RoleSkillAssign,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Assign skills to role"""
    try:
        role = role_service.assign_skills(db, role_id, data.skill_ids)
        audit_service.log(db, admin.id, "update", "role", role_id, {"action": "assign_skills", "skill_ids": data.skill_ids})
        return success_response(message="Skills assigned")
    except ValueError as e:
        return error_response(message=str(e))


@router.put("/{role_id}/tools")
async def assign_tools(
    role_id: int,
    data: RoleToolAssign,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Assign tools to role"""
    try:
        role = role_service.assign_tools(db, role_id, data.tool_ids)
        audit_service.log(db, admin.id, "update", "role", role_id, {"action": "assign_tools", "tool_ids": data.tool_ids})
        return success_response(message="Tools assigned")
    except ValueError as e:
        return error_response(message=str(e))
